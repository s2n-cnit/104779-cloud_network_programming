from datetime import datetime
from typing import Type

from app import app
from fastapi import HTTPException, status
from model import Result, ResultType, Room, User, UserRoom, engine
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, select
from check import check_user_joined_room

def joined(room_id: str, user_id: str):
    return f"User {user_id} joined room {room_id}"


def left(room_id: str, user_id: str):
    return f"User {user_id} left room {room_id}"


@app.post("/user/{user_id}/join/room/{room_id}", tags=["User - Room"])
@app.post("/room/{room_id}/join/user/{user_id}", tags=["User - Room"])
async def join_user(room_id: str, user_id: str) -> Result[UserRoom]:
    try:
        with Session(engine) as session:
            try:
                if not check_user_joined_room(user_id, room_id):
                    ur = UserRoom(
                        user_id=user_id, room_id=room_id, join_at=datetime.now()
                    )
                    session.add(ur)
                    session.commit()
                    session.refresh(ur)
                    return Result(detail=joined(room_id, user_id), data=ur)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=joined(room_id, user_id),
                    )
            except IntegrityError as ie:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.delete("/user/{user_id}/leave/room/{room_id}", tags=["User - Room"])
@app.delete("/room/{room_id}/leave/user/{user_id}", tags=["User - Room"])
async def leave_user(room_id: str, user_id: str) -> Result[UserRoom]:
    try:
        with Session(engine) as session:
            check_user_joined_room(user_id, room_id, raise_exception=True)
            ur = session.exec(
                select(UserRoom).where(
                    UserRoom.room_id == room_id and UserRoom.user_id == user_id
                )
            ).one_or_none()
            session.delete(ur)
            session.commit()
            return Result(detail=left(room_id, user_id), data=ur)
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
