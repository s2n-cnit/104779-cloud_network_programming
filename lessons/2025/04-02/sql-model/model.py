from datetime import datetime
from typing import List

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlmodel import Field, Relationship, SQLModel, create_engine


class UserRoom(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.id", primary_key=True)
    room_id: str = Field(foreign_key="room.id", primary_key=True)
    join_at: datetime


class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    first_name: str
    last_name: str
    email: str = Field(sa_column=Column("email", String, unique=True))
    creation_at: datetime = Field(default=datetime.now())
    is_active: bool = Field(default=False)
    bio: str | None = None
    age: int | None = None

    rooms: list["Room"] = Relationship(
        back_populates="users", link_model=UserRoom
    )
    messages: list["Message"] = Relationship(back_populates="user")


class Room(SQLModel, table=True):
    id: str = Field(primary_key=True)
    max_user: int | None = None
    creation_at: datetime = Field(default=datetime.now())

    users: List[User] = Relationship(
        back_populates="rooms", link_model=UserRoom
    )
    messages: List["Message"] = Relationship(back_populates="room")


class Message(SQLModel, table=True):
    id: int = Field(
        sa_column=Column("id", Integer, primary_key=True, autoincrement=True)
    )
    user_id: str = Field(foreign_key="user.id")
    room_id: str = Field(foreign_key="room.id")
    sent_at: datetime = Field(default=datetime.now())
    content: str

    user: User = Relationship(back_populates="messages")
    room: Room = Relationship(back_populates="messages")


class Result[Type: SQLModel](BaseModel):
    success: bool
    detail: str
    timestamp: datetime
    data: Type

    def __init__(
        self: "Result[Type]",
        detail: str,
        data: str,
        timestamp: datetime = datetime.now(),
        success: bool = True,
    ) -> "Result[Type]":
        super().__init__(
            success=success, detail=detail, timestamp=timestamp, data=data
        )\


class ResultType[Type: SQLModel]:
    CREATED: str = "created"
    DELETED: str = "deleted"
    UPDATED: str = "updated"

    def NOT_FOUND(id: str) -> str:
        return f"{Type} with id={id} not found"


sqlite_file_name = "yacr.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)
