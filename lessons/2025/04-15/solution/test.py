from sqlmodel import SQLModel, Field, Session, select
from typing import Self
from fastapi import FastAPI, status
from sqlalchemy.exc import IntegrityError

class Category(SQLModel, table=True):
    id: str = Field(
        sa_column=Column("id", String, primary_key=True)
    )

class Tag(SQLModel, table=True):
    commands: List[tag] = Relationship(
        back_populates="commands",
        sa_relationship_kwargs={
            "primaryjoin": "CommandTag.tag_id=tag.id",
            "link_model": CommandTag,
            "lazy": "joined",
        },
    )


class Command(SQLModel, table=True):
    id = Field(
        sa_column=Column("id", Integer, primary_key=True, autoincrement=True)
    )
    path: str
    completate_date: datetime | None = Field(default=None)
    category_id: int = Field(foreign_key="category.id")

    tags: List[Tag] = Relationship(
        back_populates="commands",
        sa_relationship_kwargs={
            "primaryjoin": "CommandTag.command_id=Command.id",
            "link_model": CommandTag,
            "lazy": "joined",
        },
    )

    workflows: List[Workflow] = Relationship(
        back_populates="commands",
        sa_relationship_kwargs={
            "primaryjoin": "WorkflowCommand.command_id=Command.id",
            "link_model": WorkflowCommand,
            "lazy": "joined",
        },
    )

    def start(self: Self):
        pass

    def stop(self: Self):
        pass

class CommandTag(SQLModel, table=True):
    tag_id: int = Field(foreign_key="tag.id")
    command_id: int = Field(foreign_key="command.id")


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

    def start():
        ...

    def stop():
        ...

class WorkflowCommand(SQLModel, table=True):
    workflow_id: int = Field(foreign_key="workflow.id")
    command_id: int = Field(foreign_key="command.id")

class Result(SQLModel):
    error: bool
    detail: str

db_path = "test.db"
engine = create_engine(f"sqlite:///{db_path}", echo=echo_engine)
SQLModel.metadata.create_all(engine)

app = FastApi()

@app.get("/category/{category_id}")
async def get_category(category_id: int) -> Category:
    try:
        with Session(engine) as session:
            category = session.exec(select(Category).where(Category.id == category_id)).one_or_none()
            if category is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND,
                                    detail=f"Category {category_id} not found")
            return category
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

@app.put("/category/{category_id}")
async def update_category(category_id: int, category: Category) -> Result:
    try:
        stored_category = get_category(category_id)
        with Session(engine) as session:
            try:
                if category.id is not None:
                    stored_category.id = category.id
                session.add(stored_category)
                session.commit()
                session.refresh(stored_category)
                return Result(error=False,
                              detail=f"Category {category_id} updated")
            except IntegrityError as ie:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

@app.get("/command")
async def get_command():
    try:
        with Session(engine) as session:
            return session.exec(select(Command)).all()
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

@app.get("/command/{command_id}")
async def get_command(command_id: int) -> Command:
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
        get_category(command.category_id)
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
        stored_command = get_command(command.id)
        with Session(engine) as session:
            try:
                if command.path is not None:
                    stored_command.path = command.path
                if command.category_id is not None:
                    stored_command.category_id = command.category_id
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
        command = get_command(command_id)
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

