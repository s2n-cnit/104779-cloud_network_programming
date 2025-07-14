from datetime import datetime
from typing import List, Optional, Self, Annotated
from pydantic import BeforeValidator
from config import db_path, echo_engine
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlmodel import (Field, Relationship, SQLModel,
                      create_engine)
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


# ReportHistory


class ReportHistoryCreate(SQLModel):
    city_id: int = Field(foreign_key="city.id")
    report_id: int = Field(foreign_key="report.id")
    start_date:Annotated[datetime, BeforeValidator(datetime_check)]
    end_date:Annotated[datetime, BeforeValidator(datetime_check)]
    measure: float

class ReportHistoryUpdate(SQLModel):
    start_date: Optional[Annotated[str, BeforeValidator(datetime_check)]] = None
    end_date: Optional[Annotated[str, BeforeValidator(datetime_check)]] = None
    measure: Optional[int] = None

class ReportHistoryPublic(ReportHistoryCreate, BasePublic):
    id: int = Field(
        sa_column=Column("id", Integer, primary_key=True, autoincrement=True)
    )


class ReportHistory(ReportHistoryPublic, table=True):
    __tablename__ = "report_history"
    __table_args__ = (
        UniqueConstraint(
            "report_id",
            "city_id",
            "start_date",
            "end_date",
            "measure"
        ),
    )
    report: "Report" = Relationship(
        back_populates="report_history",
        sa_relationship_kwargs={
            "primaryjoin": "ReportHistory.report_id==Report.id",
            "lazy": "selectin",
        },
    )
    city: "City" = Relationship(
        back_populates="report_history",
        sa_relationship_kwargs={
            "primaryjoin": "ReportHistory.city_id==City.id",  # noqa: E501
            "lazy": "selectin",
        },
    )
    created_by: "User" = Relationship(
        back_populates="report_history_created",
        sa_relationship_kwargs={
            "primaryjoin": "ReportHistory.created_by_id==User.id",
            "lazy": "selectin",
        },
    )
    updated_by: "User" = Relationship(
        back_populates="report_history_updated",
        sa_relationship_kwargs={
            "primaryjoin": "ReportHistory.updated_by_id==User.id",
            "lazy": "selectin",
        },
    )


# City


class CityCreate(SQLModel):
    name: str
    latitude: float
    longitude: float
    country_id: int = Field(foreign_key="country.id")


class CityUpdate(SQLModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_id: Optional[int] = Field(default=None, foreign_key="country.id")


class CityPublic(CityCreate, BasePublic):
    id: int = Field(
        sa_column=Column("id", Integer, primary_key=True, autoincrement=True)
    )


class City(CityPublic, table=True):
    country: "Country" = Relationship(
        back_populates="citys",
        sa_relationship_kwargs={
            "primaryjoin": "City.country==Country.id",
            "lazy": "selectin",
        },
    )
    report_history: List["ReportHistory"] = Relationship(
        back_populates="city",
        sa_relationship_kwargs={
            "primaryjoin": "ReportHistory.city_id==City.id",
            "lazy": "selectin",
        },
    )
    created_by: "User" = Relationship(
        back_populates="citys_created",
        sa_relationship_kwargs={
            "primaryjoin": "City.created_by_id==User.id",
            "lazy": "selectin",
        },
    )
    updated_by: "User" = Relationship(
        back_populates="citys_updated",
        sa_relationship_kwargs={
            "primaryjoin": "City.updated_by_id==User.id",
            "lazy": "selectin",
        },
    )


# Report


class ReportCreate(SQLModel):
    name: str
    description: str
    unit: sr


class ReportUpdate(ReportCreate):
    name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None


class ReportPublic(ReportCreate, BasePublic):
    id: int = Field(
        sa_column=Column("id", Integer, primary_key=True, autoincrement=True)
    )


class Report(ReportPublic, table=True):
    __tablename__ = "report"
    report_history: List["ReportHistory"] = Relationship(
        back_populates="report",
        sa_relationship_kwargs={
            "primaryjoin": "ReportHistory.report_id==Report.id",  # noqa: E501
            "lazy": "selectin",
        },
    )
    created_by: "User" = Relationship(
        back_populates="reports_created",
        sa_relationship_kwargs={
            "primaryjoin": "Report.created_by_id==User.id",
            "lazy": "selectin",
        },
    )
    updated_by: "User" = Relationship(
        back_populates="reports_updated",
        sa_relationship_kwargs={
            "primaryjoin": "Report.updated_by_id==User.id",
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
    citys_created: List["City"] = Relationship(
        back_populates="created_by",
        sa_relationship_kwargs={
            "primaryjoin": "City.created_by_id==User.id",
            "lazy": "selectin",
        },
    )
    reports_created: List["Report"] = Relationship(
        back_populates="created_by",
        sa_relationship_kwargs={
            "primaryjoin": "Report.created_by_id==User.id",
            "lazy": "selectin",
        },
    )
    report_history_created: List["ReportHistory"] = Relationship(
        back_populates="created_by",
        sa_relationship_kwargs={
            "primaryjoin": "ReportHistory.created_by_id==User.id",
            "lazy": "selectin",
        },
    )
    countries_created: List["Country"] = Relationship(
        back_populates="created_by",
        sa_relationship_kwargs={
            "primaryjoin": "Country.created_by_id==User.id",
            "lazy": "selectin",
        },
    )

    countries_updated: List["City"] = Relationship(
        back_populates="updated_by",
        sa_relationship_kwargs={
            "primaryjoin": "City.updated_by_id==User.id",
            "lazy": "selectin",
        },
    )
    reports_updated: List["Report"] = Relationship(
        back_populates="updated_by",
        sa_relationship_kwargs={
            "primaryjoin": "Report.updated_by_id==User.id",
            "lazy": "selectin",
        },
    )
    report_history_updated: List["ReportHistory"] = Relationship(
        back_populates="updated_by",
        sa_relationship_kwargs={
            "primaryjoin": "ReportHistory.updated_by_id==User.id",
            "lazy": "selectin",
        },
    )
    countries_updated: List["Country"] = Relationship(
        back_populates="updated_by",
        sa_relationship_kwargs={
            "primaryjoin": "Country.updated_by_id==User.id",
            "lazy": "selectin",
        },
    )


# Country


class CountryCreate(SQLModel):
    name: str


class CountryUpdate(SQLModel):
    name: Optional[str] = None


class CountryPublic(CountryCreate, BasePublic):
    id: int = Field(
        sa_column=Column("id", Integer, primary_key=True, autoincrement=True)
    )


class Country(CountryPublic, table=True):
    __tablename__ = "country"
    citys: List[City] = Relationship(
        back_populates="country",
        sa_relationship_kwargs={
            "primaryjoin": "City.country_id==Country.id",
            "lazy": "selectin",
        },
    )
    created_by: "User" = Relationship(
        back_populates="countries_created",
        sa_relationship_kwargs={
            "primaryjoin": "Country.created_by_id==User.id",
            "lazy": "selectin",
        },
    )
    updated_by: "User" = Relationship(
        back_populates="countries_updated",
        sa_relationship_kwargs={
            "primaryjoin": "Country.updated_by_id==User.id",
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
