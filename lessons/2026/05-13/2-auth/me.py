from datetime import datetime
from typing import Annotated, List

from auth import RoleChecker
from fastapi import APIRouter, Depends, HTTPException, status
from model import Message, Result, Room, User, UserRoom, engine
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

router = APIRouter(prefix="/me", tags=["Me"])


@router.post("/message", tags=["User"], summary="Write a new message in a chat room")
async def me_message_create(
    current_user: Annotated[
        User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
    ],
    message: Message
) -> Result[Message]:
    try:
        with Session(engine) as session:
            try:
                message.user_id = current_user.id
                if message.room_id not in map(lambda r: r.id, current_user.rooms):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"User {message.user_id} not joined to room {message.room_id}"
                    )
                session.add(message)
                session.commit()
                session.refresh(message)
                return Result("Message created", data=message)
            except IntegrityError as ie:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/message/{message_id}", tags=["User"], summary="Write a new message in a chat room")
async def me_message_edit(
    current_user: Annotated[
        User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
    ],
    message_id: int, message: Message
) -> Result[Message]:
    try:
        with Session(engine) as session:
            try:
                for m in current_user.messages:
                    if m.id == message_id:
                        m.content = message.content
                        m.updated_at = datetime.now()
                        session.add(m)
                        session.commit()
                        session.refresh(m)
                        return Result("Message updated", data=m)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Message {message_id} not found"
                )
            except IntegrityError as ie:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/", tags=["User"], summary="Get my details")
async def me_get(
    current_user: Annotated[
        User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
    ],
) -> User:
    return current_user


@router.delete("/", tags=["User"], summary="Remove my account")
async def me_delete(
    current_user: Annotated[
        User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
    ],
) -> User:
    try:
        with Session(engine) as session:
            session.delete(current_user)
            session.commit()
            return Result(
                detail="You was removed from yacr", data=current_user
            )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get(
    "/message",
    tags=["Message"],
    summary="Get all the messages sent by you in all chat rooms",
)
async def me_messages(
    current_user: Annotated[
        User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
    ]
) -> List[Message]:
    return current_user.messages


@router.get(
    "/room",
    tags=["Room"],
    summary="Get all the chat rooms where you are joined",
)
async def me_rooms(
    current_user: Annotated[
        User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
    ]
) -> List[Room]:
    return current_user.rooms


@router.get(
    "/room/{room_id}/message",
    tags=["Room", "Message"],
    summary="Get all the messages sent in chat room where you are joined",
)
async def me_room_messages(
    current_user: Annotated[
        User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
    ],
    room_id: str,
) -> List[Message]:
    try:
        with Session(engine) as session:
            return session.exec(
                select(Message).where(room_id in current_user.rooms)
            ).all()
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/room/{room_id}", tags=["Room"], summary="Join to the chat rooms"
)
async def me_join(
    current_user: Annotated[
        User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
    ],
    room_id: str,
) -> Result[UserRoom]:
    if room_id in map(lambda r: r.id, current_user.rooms):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You are already joined in room {room_id}",
        )
    try:
        with Session(engine) as session:
            try:
                # check if the room id exists in the YACR
                ur = UserRoom(
                    user_id=current_user.id,
                    room_id=room_id,
                    join_at=datetime.now(),
                )
                session.add(ur)
                session.commit()
                session.refresh(ur)
                return Result(
                    detail=f"You are joined to room {room_id}", data=ur
                )
            except IntegrityError as ie:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=str(ie)
                )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete(
    "/room/{room_id}",
    tags=["Me", "Room"],
    summary="Leave a chat room",
)
async def me_leave(
    current_user: Annotated[
        User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
    ],
    room_id: str,
) -> Result[UserRoom]:
    if room_id not in map(current_user.rooms, lambda r: r.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You are not joined in room {room_id}",
        )
    try:
        with Session(engine) as session:
            ur = session.exec(
                select(UserRoom).where(
                    UserRoom.room_id == room_id
                    and UserRoom.user_id == current_user.id
                )
            ).one_or_none()
            if ur is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"You are not joined to room {room_id}",
                )
            else:
                session.delete(ur)
                session.commit()
                return Result(detail=f"You are leaved room {room_id}", data=ur)
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
