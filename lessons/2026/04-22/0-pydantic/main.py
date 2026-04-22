from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

rooms = {}


class User(BaseModel):
    name: str


class Room(BaseModel):
    name: str


class Result(BaseModel):
    success: bool
    detail: str


class Message(BaseModel):
    id: str = None
    timestamp: datetime = None
    content: str
    user: User


class MessagePublic(Message):
    pass


class MessageCreate(BaseModel):
    content: str


class MessageUpdate(MessageCreate):
    id: str
    pass


@app.post("/join", tags=["User"])
def join_user_to_room(user: User, room: Room) -> Result:
    if room.name not in rooms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"room {room.name} not found",
        )
    elif user.name in rooms[room.name]["users"]:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="user {user.name} already joined in room {room.name}",
        )
    else:
        rooms[room.name]["users"].append(user)
        return Result(
            success=True, detail=f"user {user.name} joined to room {room.name}"
        )


@app.post("/leave", tags=["User"])
def leave_user_from_room(user: User, room: Room) -> Result:
    if room.name not in rooms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"room {room.name} not found",
        )
    elif user.name not in rooms[room.name]["users"]:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="user {user.name} not joined in room {room.name}",
        )
    else:
        rooms[room.name]["users"].remove(user)
        return Result(
            success=True, detail=f"user {user.name} left the room {room.name}"
        )


@app.get("/messages", tags=["Message"])
def get_all_messages_from_room(user: User, room: Room) -> list[MessagePublic]:
    if room.name not in rooms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"room {room.name} not found",
        )
    if user.name not in rooms[room.name]["users"]:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=f"user {user.name} not joined in room {room.name}",
        )
    return list(rooms[room.name]["messages"].values())


@app.post("/message", tags=["Message"])
def create_message_in_room(user: User, room: Room, message: MessageCreate) -> Result:
    if room.name not in rooms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"room {room.name} not found",
        )
    if user.name not in rooms[room.name]["users"]:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=f"user {user.name} not joined in room {room.name}",
        )

    id = str(uuid.uuid4())
    rooms[room.name]["messages"][id] = Message(id=id,
                                               content=message.content,
                                               timestamp=datetime.now(),
                                               user=user)
    return Result(
        success=True,
        detail=f"user {user.name} sent message {message.content} to room {room.name}",
    )


@app.put("/message", tags=["Message"])
def update_message(user: User, room: Room, message: MessageUpdate) -> Result:
    if room.name not in rooms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"room {room.name} not found",
        )
    if user.name not in rooms[room.name]["users"]:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=f"user {user.name} not joined in room {room.name}",
        )

    if message.id not in rooms[room.name]["messages"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"message {message.id} not found",
        )
    m = rooms[room.name]["messages"][message.id]
    if m.user.name != user.name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {user.name} not owner of message {message.id}",
        )
    m.content = message.content
    return Result(
        success=True,
        detail=f"user {user.name} edited message {m.id}",
    )


@app.delete("/message/{id}", tags=["Message"])
def delete_message(user: User, room: Room, id: str) -> Result:
    if room.name not in rooms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"room {room.name} not found",
        )
    if user.name not in rooms[room.name]["users"]:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=f"user {user.name} not joined in room {room.name}",
        )
    if id not in rooms[room.name]["messages"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"message {id} not found",
        )
    m = rooms[room.name]["messages"]
    if m.user.name != user.name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {user.name} not owner of message {m.id}",
        )
    del rooms[room.name]["messages"][id]
    return Result(
        success=True,
        detail=f"user {user.name} deleted message {m.id}",
    )


@app.post("/room", tags=["Room"])
def create_room(user: User, room: Room) -> Result:
    if room.name in rooms:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"room {room.name} already found",
        )
    # rooms[room.name] = dict(users=[user.name], messages=dict())
    rooms[room.name] = {"users": [user.name], "messages": dict()}
    return Result(
        success=True, detail=f"user {user.name} create room {room.name}"
    )


@app.get("/rooms", tags=["Room"])
def get_all_rooms() -> list[str]:
    return list(rooms.keys())


@app.delete("/room", tags=["Room"])
def delete_room(user: User, room: Room) -> Result:
    if room.name not in rooms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"room {room.name} not found",
        )
    if user.name not in rooms[room.name]["users"]:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=f"user {user.name} not joined in room {room.name}",
        )
    del rooms[room.name]
    return Result(
        success=True, detail=f"user {user.name} deletes room {room.name}"
    )
