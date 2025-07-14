from datetime import datetime
from typing import List, Optional, Self, Annotated
from pydantic import BeforeValidator
from config import db_path, echo_engine
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlmodel import (Field, Relationship, SQLModel,
                      create_engine, UniqueConstraint)
from utils import datetime_check


# Base


class BasePublic(SQLModel):
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
    )
    created_by_id: Optional[str] = Field(foreign_key="user.id")
    updated_by_id: Optional[str] = Field(foreign_key="user.id")


# History


class HistoryCreate(SQLModel):
    player_id: int = Field(foreign_key="player.id")
    team_id: int = Field(foreign_key="team.id")
    start_date: Annotated[datetime, BeforeValidator(datetime_check)]
    end_date: Annotated[datetime, BeforeValidator(datetime_check)]


class HistoryUpdate(SQLModel):
    start_date: Optional[Annotated[datetime, BeforeValidator(datetime_check)]] = None
    end_date: Optional[Annotated[datetime, BeforeValidator(datetime_check)]] = None


class HistoryPublic(HistoryCreate, BasePublic):
    id: int = Field(
        sa_column=Column("id", Integer, primary_key=True, autoincrement=True)
    )


class History(HistoryPublic, table=True):
    __tablename__ = "history"
    __table_args__ = (
        UniqueConstraint(
            "team_id",
            "player_id",
            "start_date",
            "end_date"
        ),
    )
    team: "Team" = Relationship(
        back_populates="history",
        sa_relationship_kwargs={
            "primaryjoin": "History.team_id==Team.id",
            "lazy": "selectin",
        },
    )
    player: "Player" = Relationship(
        back_populates="history",
        sa_relationship_kwargs={
            "primaryjoin": "History.player_id==Player.id",  # noqa: E501
            "lazy": "selectin",
        },
    )
    created_by: "User" = Relationship(
        back_populates="history_created",
        sa_relationship_kwargs={
            "primaryjoin": "History.created_by_id==User.id",
            "lazy": "selectin",
        },
    )
    updated_by: "User" = Relationship(
        back_populates="history_updated",
        sa_relationship_kwargs={
            "primaryjoin": "History.updated_by_id==User.id",
            "lazy": "selectin",
        },
    )


# Player


class PlayerCreate(SQLModel):
    name: str
    birth_date: Annotated[datetime, BeforeValidator(datetime_check)]
    player_role_id: int = Field(foreign_key="player_role.id")


class PlayerUpdate(SQLModel):
    name: Optional[str] = None
    birth_date: Optional[Annotated[datetime, BeforeValidator(datetime_check)]] = None
    player_role_id: Optional[int] = Field(default=None, foreign_key="player_role.id")


class PlayerPublic(PlayerCreate, BasePublic):
    id: int = Field(
        sa_column=Column("id", Integer, primary_key=True, autoincrement=True)
    )


class Player(PlayerPublic, table=True):
    player_role: "PlayerRole" = Relationship(
        back_populates="players",
        sa_relationship_kwargs={
            "primaryjoin": "Player.player_role_id==PlayerRole.id",
            "lazy": "selectin",
        },
    )
    history: List["History"] = Relationship(
        back_populates="player",
        sa_relationship_kwargs={
            "primaryjoin": "History.player_id==Player.id",
            "lazy": "selectin",
        },
    )
    created_by: "User" = Relationship(
        back_populates="players_created",
        sa_relationship_kwargs={
            "primaryjoin": "Player.created_by_id==User.id",
            "lazy": "selectin",
        },
    )
    updated_by: "User" = Relationship(
        back_populates="players_updated",
        sa_relationship_kwargs={
            "primaryjoin": "Player.updated_by_id==User.id",
            "lazy": "selectin",
        },
    )


# Team


class TeamCreate(SQLModel):
    name: str
    year_foundation: int
    city: str


class TeamUpdate(TeamCreate):
    name: Optional[str] = None
    year_foundation: Optional[int] = None
    city: Optional[str] = None


class TeamPublic(TeamCreate, BasePublic):
    id: int = Field(
        sa_column=Column("id", Integer, primary_key=True, autoincrement=True)
    )


class Team(TeamPublic, table=True):
    __tablename__ = "team"
    history: List["History"] = Relationship(
        back_populates="team",
        sa_relationship_kwargs={
            "primaryjoin": "History.team_id==Team.id",  # noqa: E501
            "lazy": "selectin",
        },
    )
    created_by: "User" = Relationship(
        back_populates="teams_created",
        sa_relationship_kwargs={
            "primaryjoin": "Team.created_by_id==User.id",
            "lazy": "selectin",
        },
    )
    updated_by: "User" = Relationship(
        back_populates="teams_updated",
        sa_relationship_kwargs={
            "primaryjoin": "Team.updated_by_id==User.id",
            "lazy": "selectin",
        },
    )


# Role


class RoleCreate(SQLModel):
    id: str = Field(primary_key=True)
    description: Optional[str] = None


class RoleUpdate(SQLModel):
    description: Optional[str] = None


class RolePublic(RoleCreate, BasePublic):
    pass


class Role(RolePublic, table=True):
    pass


# User


class UserCreate(SQLModel):
    id: str = Field(primary_key=True)
    first_name: str
    last_name: str
    email: str = Field(sa_column=Column("email", String, unique=True))
    password: str
    role_id: str = Field(foreign_key="role.id")
    disabled: bool = False
    bio: Optional[str] = None
    age: Optional[int] = None


class UserUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = Field(
        default=None, sa_column=Column("email", String, unique=True)
    )
    password: Optional[str]
    role_id: Optional[str] = Field(default=None, foreign_key="role.id")
    disabled: Optional[bool] = False
    bio: Optional[str] = None
    age: Optional[int] = None


class UserPublic(BasePublic):
    id: str = Field(primary_key=True)
    first_name: str
    last_name: str
    email: str = Field(sa_column=Column("email", String, unique=True))
    role_id: str = Field(foreign_key="role.id")
    disabled: bool = False
    bio: Optional[str] = None
    age: Optional[int] = None


class User(UserCreate, BasePublic, table=True):
    players_created: List["Player"] = Relationship(
        back_populates="created_by",
        sa_relationship_kwargs={
            "primaryjoin": "Player.created_by_id==User.id",
            "lazy": "selectin",
        },
    )
    teams_created: List["Team"] = Relationship(
        back_populates="created_by",
        sa_relationship_kwargs={
            "primaryjoin": "Team.created_by_id==User.id",
            "lazy": "selectin",
        },
    )
    history_created: List["History"] = Relationship(
        back_populates="created_by",
        sa_relationship_kwargs={
            "primaryjoin": "History.created_by_id==User.id",
            "lazy": "selectin",
        },
    )
    player_roles_created: List["PlayerRole"] = Relationship(
        back_populates="created_by",
        sa_relationship_kwargs={
            "primaryjoin": "PlayerRole.created_by_id==User.id",
            "lazy": "selectin",
        },
    )

    players_updated: List["Player"] = Relationship(
        back_populates="updated_by",
        sa_relationship_kwargs={
            "primaryjoin": "Player.updated_by_id==User.id",
            "lazy": "selectin",
        },
    )
    teams_updated: List["Team"] = Relationship(
        back_populates="updated_by",
        sa_relationship_kwargs={
            "primaryjoin": "Team.updated_by_id==User.id",
            "lazy": "selectin",
        },
    )
    history_updated: List["History"] = Relationship(
        back_populates="updated_by",
        sa_relationship_kwargs={
            "primaryjoin": "History.updated_by_id==User.id",
            "lazy": "selectin",
        },
    )
    player_roles_updated: List["PlayerRole"] = Relationship(
        back_populates="updated_by",
        sa_relationship_kwargs={
            "primaryjoin": "PlayerRole.updated_by_id==User.id",
            "lazy": "selectin",
        },
    )


# PlayerRole


class PlayerRoleCreate(SQLModel):
    name: str


class PlayerRoleUpdate(SQLModel):
    name: Optional[str] = None


class PlayerRolePublic(PlayerRoleCreate, BasePublic):
    id: int = Field(
        sa_column=Column("id", Integer, primary_key=True, autoincrement=True)
    )


class PlayerRole(PlayerRolePublic, table=True):
    __tablename__ = "player_role"
    players: List[Player] = Relationship(
        back_populates="player_role",
        sa_relationship_kwargs={
            "primaryjoin": "Player.player_role_id==PlayerRole.id",
            "lazy": "selectin",
        },
    )
    created_by: "User" = Relationship(
        back_populates="player_roles_created",
        sa_relationship_kwargs={
            "primaryjoin": "PlayerRole.created_by_id==User.id",
            "lazy": "selectin",
        },
    )
    updated_by: "User" = Relationship(
        back_populates="player_roles_updated",
        sa_relationship_kwargs={
            "primaryjoin": "PlayerRole.updated_by_id==User.id",
            "lazy": "selectin",
        },
    )


# Result


class Result(BaseModel):
    action: str
    target: str
    id: str | int
    success: bool
    error: bool
    timestamp: datetime

    def __init__(
        self: Self,
        target: str,
        id: Optional[str | int],
        action: str,
        success: bool = True,
    ) -> Self:
        super().__init__(
            action=action,
            target=target,
            id=id,
            timestamp=datetime.now(),
            success=success,
            error=not success,
        )


# Token


class Token[Type: SQLModel](BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None


engine = create_engine(f"sqlite:///{db_path}", echo=echo_engine)
SQLModel.metadata.create_all(engine)
