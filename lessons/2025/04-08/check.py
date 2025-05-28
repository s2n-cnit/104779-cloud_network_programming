from datetime import datetime
from typing import Type

from app import app
from fastapi import HTTPException, status
from model import Result, ResultType, Room, User, UserRoom, engine
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, select

def not_joined(room_id: str, user_id: str):
    return f"User {user_id} not joined room {room_id}"

def check_entity(
    session: Session, Entity: Type[SQLModel], entity_id: str
) -> None:
    if (
        session.exec(select(Entity).where(Entity.id == entity_id)).one_or_none()
        is None
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResultType[Entity].NOT_FOUND(entity_id)
        )

def check_user_joined_room(
    session: Session, user_id: str, room_id: str, raise_exception: bool = False
) -> bool | None:
    check_entity(session, User, user_id)
    check_entity(session, Room, room_id)
    ur = session.exec(
        select(UserRoom).where(
            UserRoom.room_id == room_id and UserRoom.user_id == user_id
        )
    ).one_or_none()
    if ur is None:
        if raise_exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=not_joined(room_id, user_id),
            )
        else:
            return False
    return True
