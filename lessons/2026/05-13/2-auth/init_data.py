from datetime import datetime

from model import Role, Room, User, UserRoom, engine
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

data_roles = dict(admin={"id": "admin"}, user={"id": "user"})

data_users = dict(
    admin={
        "id": "admin",
        "first_name": "Super",
        "last_name": "Admin",
        "email": "admin@yacr.com",
        "password": pwd_context.hash("admin"),
        "disabled": False,
        "creation_at": datetime.now(),
        "role_id": "admin",
        "bio": "YACR Admin",
        "age": 50,
    },
    alexcarrega={
        "id": "alexcarrega",
        "first_name": "Alex",
        "last_name": "Carrega",
        "email": "contact@alexcarrega.com",
        "password": pwd_context.hash("test-me"),
        "disabled": False,
        "creation_at": datetime.now(),
        "role_id": "user",
        "bio": "PhD, IT & Network Engineer",
        "age": 42,
    },
)


def insert_role(key):
    try:
        role = Role(**data_roles[key])
        print(role)
        with Session(engine) as session:
            try:
                session.add(role)
                session.commit()
                session.refresh(role)
                print(f"Role {role.id} created")
            except IntegrityError as ie:
                print(f"Error: {ie}")
    except Exception as e:
        print(f"Error: {e}")


def insert_user(key):
    try:
        user = User(**data_users[key])
        print(user)
        with Session(engine) as session:
            try:
                session.add(user)
                session.commit()
                session.refresh(user)
                print(f"User {user.id} created")
            except IntegrityError as ie:
                print(f"Error: {ie}")
    except Exception as e:
        print(f"Error: {e}")


def insert_rooms():
    for r in ["football", "basket", "cinema", "music"]:
        room = Room(id=r)
        print(room)
        with Session(engine) as session:
            try:
                session.add(room)
                session.commit()
                session.refresh(room)
                print(f"Room {room.id} created")
            except IntegrityError as ie:
                print(f"Error: {ie}")
            except Exception as e:
                print(f"Error: {e}")


insert_role("admin")
insert_role("user")
insert_user("admin")
insert_user("alexcarrega")

insert_rooms()


def join_room(user_id: str, room_id: str):
    ur = UserRoom(user_id=user_id, room_id=room_id, join_at=datetime.now())
    print()
    with Session(engine) as session:
        try:
            session.add(ur)
            session.commit()
            session.refresh(ur)
            print(f"User {user_id} joined to room {room_id}")
        except IntegrityError as ie:
            print(f"Error: {ie}")
        except Exception as e:
            print(f"Error: {e}")


join_room(user_id="alexcarrega", room_id="music")
