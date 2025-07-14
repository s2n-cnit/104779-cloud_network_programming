from enum import Enum
from typing import List

from db import DB
from error import NotEmptyException
from fastapi import APIRouter
from model import Player, Result, PlayerUpdate, PlayerCreate, PlayerPublic
from router.player_role import _pr
from router.lib import BasicUser, is_admin, prefix

LABEL = "Player"
_t = [LABEL]
_player = DB[Player](Player, LABEL)
router = APIRouter(prefix=f"/{LABEL.lower()}", tags=_t)


class _s(str, Enum):
    CREATE = "Insert a new player"
    READ_ALL = "Get all the players"
    READ = "Get the details of a player"
    UPDATE = "Update a player"
    DELETE = "Delete a player"


@router.post(prefix(), tags=_t, summary=_s.CREATE)
async def create(user: BasicUser, player: PlayerCreate) -> Result:
    _pr.read(player.player_role_id)
    return _player.create(player, user)


@router.get(prefix(), tags=_t, summary=_s.READ_ALL)
async def read_all(user: BasicUser) -> List[PlayerPublic]:
    if is_admin(user):
        return _player.read_all()
    else:
        return user.players_created


@router.get(prefix(id=True), tags=_t, summary=_s.READ)
async def read(user: BasicUser, id: int) -> PlayerPublic:
    if is_admin(user):
        return _player.read(id)
    else:
        return _player.read_personal(id, user.players_created)


@router.put(prefix(id=True), tags=_t, summary=_s.UPDATE)
async def update(user: BasicUser, id: int, player: PlayerUpdate) -> Result:
    if is_admin(user):
        _player.read(id)
    else:
        _player.read_personal(id, user.players_created)
    if player.player_role_id is not None:
        _pr.read(player.player_role_id)
    return _player.update(id, player, user)


@router.delete(prefix(id=True), tags=_t, summary=_s.DELETE)
async def delete(user: BasicUser, id: int) -> Result:
    if is_admin(user):
        player = _player.read(id)
    else:
        player = _player.read_personal(id, user.players_created)
    if len(player.history) > 0:
        raise NotEmptyException(LABEL, id)
    return _player.delete(id)
