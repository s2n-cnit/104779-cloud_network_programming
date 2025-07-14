from enum import Enum
from typing import List

from db import DB
from error import NotEmptyException
from fastapi import APIRouter
from model import PlayerRole, PlayerRoleCreate, PlayerRolePublic, PlayerRoleUpdate, Result
from router.lib import BasicUser, prefix

LABEL = "Player Role"
_t = [LABEL]
_pr = DB[PlayerRole](PlayerRole, LABEL)
router = APIRouter(prefix=f"/{LABEL.lower().replace(" ", "-")}", tags=_t)


class _s(str, Enum):
    CREATE = "Insert a new player role"
    READ_ALL = "Get all the player roles"
    READ = "Get the details of a player role"
    UPDATE = "Update a player role"
    DELETE = "Delete a player role"


@router.post(prefix(), tags=_t, summary=_s.CREATE)
async def create(user: BasicUser, pr: PlayerRoleCreate) -> Result:
    return _pr.create(pr, user)


@router.get(prefix(), tags=_t, summary=_s.READ_ALL)
async def read_all(user: BasicUser) -> List[PlayerRolePublic]:
    return _pr.read_all()


@router.get(prefix(id=True), tags=_t, summary=_s.READ)
async def read(user: BasicUser, id: int) -> PlayerRolePublic:
    return _pr.read(id)


@router.put(prefix(id=True), tags=_t, summary=_s.UPDATE)
async def update(user: BasicUser, id: int, pr: PlayerRoleUpdate) -> Result:
    _pr.read(id)
    return _pr.update(id, pr, user)


@router.delete(prefix(id=True), tags=_t, summary=_s.DELETE)
async def delete(user: BasicUser, id: int) -> Result:
    pr = _pr.read(id)
    if len(pr.players) > 0:
        raise NotEmptyException(LABEL, id)
    return _pr.delete(id)
