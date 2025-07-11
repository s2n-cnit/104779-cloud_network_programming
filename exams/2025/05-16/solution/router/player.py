from enum import Enum
from typing import List

from db import DB
from error import NotEmptyException
from fastapi import APIRouter
from model import (PlayerRole, Player, PlayerCreate, PlayerPublic,
                   PlayerUpdate, Result)
from router.player_role import LABEL as CAT_LABEL
from router.lib import AdminUser, BasicUser, prefix

LABEL = "Player"
_t = [LABEL]
_pr = DB[PlayerRole](PlayerRole, CAT_LABEL)
_player = DB[Player](Player, LABEL)
router = APIRouter(prefix=f"/{LABEL.lower()}", tags=_t)


class _s(str, Enum):
    CREATE = "Insert a new player"
    READ_ALL = "Get all the players"
    READ = "Get the details of a player"
    UPDATE = "Update a player"
    DELETE = "Delete a player"


@router.post(prefix(), tags=_t, summary=_s.CREATE)
async def create(user: AdminUser, player: PlayerCreate) -> Result:
    _pr.read(player.player_role_id)
    return _player.create(player, user)


@router.get(prefix(), tags=_t, summary=_s.READ_ALL)
async def read_all(user: BasicUser) -> List[PlayerPublic]:
    return _player.read_all()


@router.get(prefix(id=True), tags=_t, summary=_s.READ)
async def read(user: BasicUser, id: int) -> PlayerPublic:
    return _player.read(id)


@router.put(prefix(id=True), tags=_t, summary=_s.UPDATE)
async def update(user: AdminUser, id: int, player: PlayerUpdate) -> Result:
    _player.read(id)
    if player.player_role_id is not None:
        _pr.read(player.player_role_id)
    return _player.update(id, player, user)


@router.delete(prefix(id=True), tags=_t, summary=_s.DELETE)
async def delete(user: AdminUser, id: int) -> Result:
    player = _player.read(id)
    if len(player.player_sessions) > 0:
        raise NotEmptyException(LABEL, id)
    return _player.delete(id)
