from datetime import datetime, timedelta, timezone
from typing import Annotated, List, Self

import jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import (Column, Field, Integer, Relationship, Session, SQLModel,
                      String, create_engine, select)

# id: for integer (autoincremented) primary key
# name: for string primary key


class Category(SQLModel, table=True):
    name: str = Field(
        sa_column=Column("name", String, primary_key=True)
    )

    created_by_id: str = Field(foreign_key="user.id")
    updated_by_id: str = Field(foreign_key="user.id")

    commands: List["Command"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={
            "primaryjoin": "Category.name=Command.category_name",
            "lazy": "joined",
        },
    )

    created_by: "User" = Relationship(
        back_populates="categories_created",
        sa_relationship_kwargs={
            "primaryjoin": "Category.created_by_id=User.id",
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

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "hdhfh5jdnb7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

refresh_tokens = []

ACCESS_TOKEN_EXPIRE_MINUTES = 20
REFRESH_TOKEN_EXPIRE_MINUTES = 120


class Role(SQLModel, table=True):
    id: str = Field(primary_key=True)
    description: str

    users: List["User"] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={
            "primaryjoin": "Role.id=User.ids",
            "lazy": "joined",
        },
    )


class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    password: str
    role_id: str = Field(foreign_key="role.id")
    disabled: bool = Field(default=False)

    role: Role = Relationship(
        back_populates="users",
        sa_relationship_kwargs={
            "primaryjoin": "Role.id=User.id",
            "lazy": "joined",
        },
    )

    categories_created: Category = Relationship(
        back_populates="created_by",
        sa_relationship_kwargs={
            "primaryjoin": "Category.created_by_id=User.id",
            "lazy": "joined",
        },
    )


class Token(SQLModel):  # BaseModel is similar in this case because we don't save in DB.
    access_token: str | None = None
    refresh_token: str | None = None


def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user


def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.DecodeError:
        raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def validate_refresh_token(
    token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        if token in refresh_tokens:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            role: str = payload.get("role")
            if username is None or role is None:
                raise credentials_exception
        else:
            raise credentials_exception
    except (jwt.DecodeError, ValidationError):
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user, token


class RoleChecker:
    def __init__(
        self: "RoleChecker", allowed_role_ids: List[str]
    ) -> "RoleChecker":
        self.allowed_role_ids = allowed_role_ids

    def __call__(
        self: "RoleChecker",
        user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if user.role_id in self.allowed_role_ids:
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have enough permissions",
        )


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = create_token(
        data={"sub": user.id, "role": user.role_id},
        expires_delta=access_token_expires,
    )
    refresh_token = create_token(
        data={"sub": user.id, "role": user.role_id},
        expires_delta=refresh_token_expires,
    )
    refresh_tokens.append(refresh_token)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
async def refresh_access_token(
    token_data: Annotated[tuple[User, str], Depends(validate_refresh_token)]
):
    user, token = token_data
    access_token = create_token(
        data={"sub": user.id, "role": user.role_id},
        expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    refresh_token = create_token(
        data={"sub": user.id, "role": user.role_di},
        expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    refresh_tokens.remove(token)
    refresh_tokens.append(refresh_token)
    return Token(access_token=access_token, refresh_token=refresh_token)


@app.post("/category")
async def create_category(current_user: Annotated[
            User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
        ], category: Category) -> Result:
    try:
        with Session(engine) as session:
            try:
                category.created_by_id = current_user.id
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
async def get_category_list(current_user: Annotated[
            User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
        ]) -> List[Category]:
    try:
        return current_user.categories_created
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/admin/category")
async def get_category_list_admin(current_user: Annotated[
            User, Depends(RoleChecker(allowed_role_ids=["admin"]))
        ]) -> List[Category]:
    try:
        with Session(engine) as session:
            return session.exec(select(Category)).all()
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/admin/category/{category_name}")
async def get_category_single_admin(current_user: Annotated[
            User, Depends(RoleChecker(allowed_role_ids=["admin"]))
        ], category_name: str) -> Category:
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


@app.get("/category/{category_name}")
async def get_category_single(current_user: Annotated[
            User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
        ], category_name: str) -> Category:
    try:
        for cat in current_user.categories_created:
            if cat.name == category_name:
                return cat
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f"Category {category_name} not found")
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.delete("/category/{category_name}")
async def delete_category(current_user: Annotated[
            User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
        ], category_name: str) -> Result:
    try:
        category = get_category_single(category_name)
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


@app.delete("/admin/category/{category_name}")
async def delete_category_admin(current_user: Annotated[
            User, Depends(RoleChecker(allowed_role_ids=["admin"]))
        ], category_name: str) -> Result:
    try:
        category = get_category_single_admin(category_name)
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


def __update_category(stored_category: Category, category: Category, current_user: User) -> Result:
    with Session(engine) as session:
        try:
            stored_category.name = category.name
            stored_category.updated_by_id = current_user.id
            session.add(stored_category)
            session.commit()
            session.refresh(stored_category)
            return Result(error=False,
                          detail=f"Category {category.name} updated")
        except IntegrityError as ie:
            raise HTTPException(
                status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
            )


@app.put("/category/{category_name}")
async def update_category(current_user: Annotated[
            User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
        ], category_name: str, category: Category) -> Result:
    try:
        stored_category = get_category_single(category_name)
        return __update_category(stored_category, category, current_user)
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.put("/admin/category/{category_name}")
async def update_category_admin(current_user: Annotated[
            User, Depends(RoleChecker(allowed_role_ids=["admin"]))
        ], category_name: str, category: Category) -> Result:
    try:
        stored_category = get_category_single_admin(category_name)
        return __update_category(stored_category, category, current_user)
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
