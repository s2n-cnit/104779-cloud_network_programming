from datetime import datetime
from typing import Self

from fastapi import FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import (Column, Field, Integer, Relationship, Session, SQLModel,
                      String, create_engine, select)
from Typing import List

# id: for integer (autoincremented) primary key
# name: for string primary key


class Category(SQLModel, table=True):
    name: str = Field(
        sa_column=Column("name", String, primary_key=True)
    )

    commands: List["Command"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={
            "primaryjoin": "Category.name=Command.category_name",
            "lazy": "joined",
        },
    )


class CommandTag(SQLModel, table=True):
    id = Field(
        sa_column=Column("id", Integer, primary_key=True, autoincrement=True)
    )
    tag_name: int = Field(foreign_key="tag.name")
    command_id: int = Field(foreign_key="command.id")


class WorkflowCommand(SQLModel, table=True):
    id = Field(
        sa_column=Column("id", Integer, primary_key=True, autoincrement=True)
    )
    workflow_id: int = Field(foreign_key="workflow.id")
    command_id: int = Field(foreign_key="command.id")


class Command(SQLModel, table=True):
    id = Field(
        sa_column=Column("id", Integer, primary_key=True, autoincrement=True)
    )
    path: str
    completate_date: datetime | None = Field(default=None)
    category_name: str = Field(foreign_key="category.name")

    category: Category = Relationship(
        back_populates="commands",
        sa_relationship_kwargs={
            "primaryjoin": "Category.name=Command.category_name",
            "lazy": "joined",
        },
    )

    tags: List["Tag"] = Relationship(
        back_populates="commands",
        sa_relationship_kwargs={
            "primaryjoin": "CommandTag.command_id=Command.id",
            "link_model": CommandTag,
            "lazy": "joined",
        },
    )

    workflows: List["Workflow"] = Relationship(
        back_populates="commands",
        sa_relationship_kwargs={
            "primaryjoin": "WorkflowCommand.command_id=Command.id",
            "link_model": WorkflowCommand,
            "lazy": "joined",
        },
    )

    def start(self: Self):
        started_date = datetime.now()
        print(f"Command {self.path} started at {started_date}")

    def stop(self: Self):
        self.completion_date = datetime.now()
        print(f"Command {self.path} stopped at {self.completion_date}")


class Tag(SQLModel, table=True):
    name: str = Field(
        sa_column=Column("name", String, primary_key=True)
    )
    commands: List[Command] = Relationship(
        back_populates="commands",
        sa_relationship_kwargs={
            "primaryjoin": "CommandTag.tag_id=tag.id",
            "link_model": CommandTag,
            "lazy": "joined",
        },
    )


class Workflow(SQLModel, table=True):
    id: int = Field(
        sa_column=Column("id", Integer, primary_key=True, autoincrement=True)
    )

    commands: List[Command] = Relationship(
        back_populates="workflows",
        sa_relationship_kwargs={
            "primaryjoin": "WorkflowCommand.workflow_id==Workflow.id",
            "link_model": WorkflowCommand,
            "lazy": "joined",
        },
    )

    def start(self: Self):
        print(f"Workflow {self.id} started")
        for cmd in self.commands:
            cmd.start()

    def stop(self: Self):
        for cmd in self.commands:
            cmd.stop()
        print(f"Workflow {self.id} stopped")


class Result(SQLModel):
    error: bool
    detail: str


db_path = "/test.db"
engine = create_engine(f"sqlite://{db_path}", echo=True)
SQLModel.metadata.create_all(engine)

app = FastAPI()


@app.post("/category")
async def create_category(category: Category) -> Result:
    try:
        with Session(engine) as session:
            try:
                session.add(category)
                session.commit()
                session.refresh(category)
                return Result(error=False, detail="Category created")
            except IntegrityError as ie:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/category")
async def get_category_list() -> List[Category]:
    try:
        with Session(engine) as session:
            return session.exec(select(Category)).all()
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/category/{category_name}")
async def get_category_single(category_name: str) -> Category:
    try:
        with Session(engine) as session:
            category = session.exec(select(Category).where(Category.name == category_name)).one_or_none()
            if category is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND,
                                    detail=f"Category {category_name} not found")
            return category
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.delete("/category/{category_name}")
async def delete_category(category_name: str) -> Result:
    try:
        category = get_command_single(category_name)
        if len(category.commands) > 0:
            raise HTTPException(
                status.HTTP_406_NOT_ACCEPTABLE, detail=f"Category {category.name} not empty"
            )
        with Session(engine) as session:
            try:
                session.delete(category)
                session.commit()
                session.refresh(category)
                return Result(error=False, detail=f"Category {category_name} deleted")
            except IntegrityError as ie:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.put("/category/{category_name}")
async def update_category(category_name: str, category: Category) -> Result:
    try:
        stored_category = get_category_single(category_name)
        with Session(engine) as session:
            try:
                stored_category.name = category.name
                session.add(stored_category)
                session.commit()
                session.refresh(stored_category)
                return Result(error=False,
                              detail=f"Category {category_name} updated")
            except IntegrityError as ie:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/command")
async def get_command_list() -> List[Command]:
    try:
        with Session(engine) as session:
            return session.exec(select(Command)).all()
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/command/{command_id}")
async def get_command_single(command_id: int) -> Command:
    try:
        with Session(engine) as session:
            command = session.exec(select(Command).where(Command.id == command_id)).one_or_none()
            if command is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND,
                                    detail=f"Command {command_id} not found")
            return command
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/command")
async def create_command(command: Command) -> Result:
    try:
        get_category_single(command.category_name)
        with Session(engine) as session:
            try:
                session.add(command)
                session.commit()
                session.refresh(command)
                return Result(error=False, detail="Command created")
            except IntegrityError as ie:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.put("/command")
async def update_command(command: Command) -> Result:
    try:
        stored_command = get_command_single(command.id)
        with Session(engine) as session:
            try:
                if command.path is not None:
                    stored_command.path = command.path
                if command.category_name is not None:
                    get_category_single(command.category_name)
                    stored_command.category_name = command.category_name
                session.add(stored_command)
                session.commit()
                session.refresh(stored_command)
                return Result(error=False,
                              detail=f"Command {command.id} updated")
            except IntegrityError as ie:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.delete("/command/{command_id}")
async def delete_command(command_id: int) -> Result:
    try:
        command = get_command_single(command_id)
        with Session(engine) as session:
            try:
                session.delete(command)
                session.commit()
                session.refresh(command)
                return Result(error=False, detail=f"Command {command_id} deleted")
            except IntegrityError as ie:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/workflow")
async def get_workflow_list() -> List[Workflow]:
    try:
        with Session(engine) as session:
            return session.exec(select(Workflow)).all()
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/command/{workflow_id}")
async def get_workflow_single(workflow_id: int) -> Workflow:
    try:
        with Session(engine) as session:
            command = session.exec(select(Command).where(Workflow.id == workflow_id)).one_or_none()
            if command is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND,
                                    detail=f"Workflow {workflow_id} not found")
            return command
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/workflow")
async def create_workflow(workflow: Workflow) -> Result:
    try:
        with Session(engine) as session:
            try:
                session.add(workflow)
                session.commit()
                session.refresh(workflow)
                return Result(error=False, detail="Workflow created")
            except IntegrityError as ie:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.delete("/workflow/{workflow_id}")
async def delete_workflow(workflow_id: int) -> Result:
    try:
        workflow = get_workflow_single(workflow_id)
        with Session(engine) as session:
            try:
                session.delete(workflow)
                session.commit()
                session.refresh(workflow)
                return Result(error=False, detail=f"Workflow {workflow_id} deleted")
            except IntegrityError as ie:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/workflow/{workflow_id}/command/{command_id}")
async def add_command_workflow(workflow_id: int, command_id: int) -> Result:
    try:
        with Session(engine) as session:
            workflow_cmd = session.exec(select(WorkflowCommand).where(
                WorkflowCommand.command_id == command_id and WorkflowCommand.workflow_id == workflow_id)).one_or_none()
            if workflow_cmd is not None:
                raise HTTPException(status.HTTP_409_CONFLICT,
                                    detail=f"Command {command_id} already present int Workflow {workflow_id}")
            try:
                wf = WorkflowCommand(command_id=command_id, workflow_id=workflow_id)
                session.add(wf)
                session.commit()
                session.refresh(wf)
                return Result(error=False, detail="Command {command_id} added to Workflow {workflow_id}")
            except IntegrityError as ie:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.delete("/workflow/{workflow_id}/command/{command_id}")
async def remove_command_workflow(workflow_id: int, command_id: int) -> Result:
    try:
        with Session(engine) as session:
            workflow_cmd = session.exec(select(WorkflowCommand).where(
                WorkflowCommand.command_id == command_id and WorkflowCommand.workflow_id == workflow_id)).one_or_none()
            if workflow_cmd is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND,
                                    detail=f"Command {command_id} already present int Workflow {workflow_id}")
            try:
                wf = WorkflowCommand(command_id=command_id, workflow_id=workflow_id)
                session.delete(wf)
                session.commit()
                session.refresh(wf)
                return Result(error=False, detail="Command {command_id} removed from Workflow {workflow_id}")
            except IntegrityError as ie:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.put("/workflow/{workflow_id}/start")
async def workflow_start(workflow_id: int) -> Result:
    try:
        workflow = get_workflow_single(workflow_id)
        with Session(engine) as session:
            try:
                if len(workflow.commands) == 0:
                    raise HTTPException(status.HTTP_404_NOT_FOUND,
                                        detail=f"Workflow {workflow_id} empty")
                workflow.start()
                for cmd in workflow.commands:
                    session.add(cmd)
                session.add(workflow)
                session.commit()
                session.refresh(workflow)
                return Result(error=False,
                              detail=f"Workflow {workflow.id} started")
            except IntegrityError as ie:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.put("/workflow/{workflow_id}/stop")
async def workflow_stop(workflow_id: int) -> Result:
    try:
        workflow = get_workflow_single(workflow_id)
        with Session(engine) as session:
            try:
                if len(workflow.commands) == 0:
                    raise HTTPException(status.HTTP_404_NOT_FOUND,
                                        detail=f"Workflow {workflow_id} empty")
                workflow.stop()
                for cmd in workflow.commands:
                    session.add(cmd)
                session.add(workflow)
                session.commit()
                session.refresh(workflow)
                return Result(error=False,
                              detail=f"Workflow {workflow.id} stopped")
            except IntegrityError as ie:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
