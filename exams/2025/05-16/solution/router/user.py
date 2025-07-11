from enum import Enum
from typing import List

from db import DB
from fastapi import APIRouter
from model import Result, User, UserCreate, UserPublic, UserUpdate
from router.lib import AdminUser, BasicUser, prefix

LABEL = "User"
_t = [LABEL]
_user = DB[User](User, LABEL)
router = APIRouter(prefix=f"/{LABEL.lower()}", tags=_t)


class _s(str, Enum):
    CREATE = "Insert a new user"
    READ_ALL = "Get all the users"
    READ = "Get the details of a user"
    READ_ME = "Get the details of your account"
    UPDATE = "Update a user"
    UPDATE_ME = "Update your account"
    DELETE = "Delete a user"
    DELETE_ME = "Delete your account"


@router.post(prefix(), tags=_t, summary=_s.CREATE)
async def create(admin_user: AdminUser, user: UserCreate) -> Result:
    return _user.create(user, admin_user)


@router.get(prefix(), tags=_t, summary=_s.READ_ALL)
async def read_all(user: AdminUser) -> List[UserPublic]:
    return _user.read_all()


@router.get(prefix(me=True), tags=_t, summary=_s.READ_ME)
async def read_me(user: BasicUser) -> List[UserPublic]:
    return user


@router.get(prefix(id=True), tags=_t, summary=_s.READ)
async def read(user: AdminUser, id: str) -> UserPublic:
    return _user.read(id)


@router.put(prefix(id=True), tags=_t, summary=_s.UPDATE)
async def update(admin_user: AdminUser, user: UserUpdate) -> Result:
    _user.read(id)
    return _user.update(id, user, admin_user)


@router.put(prefix(me=True), tags=_t, summary=_s.UPDATE_ME)
async def update_me(basic_user: BasicUser, user: UserUpdate) -> Result:
    return _user.update(basic_user.id, user, basic_user)


@router.delete(prefix(id=True), tags=_t, summary=_s.DELETE)
async def delete(user: AdminUser, id: str) -> Result:
    _user.read(id)
    return _user.delete(id)


@router.delete(prefix(), tags=_t, summary=_s.DELETE_ME)
async def delete_me(user: BasicUser) -> Result:
    return _user.delete(user.id)
