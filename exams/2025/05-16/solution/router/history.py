from enum import Enum
from typing import List

from db import DB
from fastapi import APIRouter
from model import (History, HistoryCreate,
                   HistoryPublic, HistoryUpdate, Result)
from router.player import _player
from router.lib import BasicUser, is_admin, prefix
from router.team import _team

LABEL = "History"

_t = [LABEL]
_hist = DB[History](History, LABEL)
router = APIRouter(prefix=f"/{LABEL.lower()}", tags=_t)


class _s(str, Enum):
    CREATE = "Insert a new record in the history of a player"
    READ = "Get the details of the history of a player"
    READ_ALL = "Get the details of the history of all the players"
    UPDATE = "Update the data about the record of the history of a player"
    DELETE = "Delete a record from the history of a player"


@router.post(prefix(), tags=_t, summary=_s.CREATE)
async def create(user: BasicUser, hist: HistoryCreate) -> Result:
    if is_admin(user):
        _team.read(hist.team_id)
        _player.read(hist.player_id)
    else:
        _team.read_personal(hist.team_id, user.teams_created)
        _player.read_personal(hist.player_id, user.players_created)
    return _hist.create(hist, user)


@router.get(prefix(), tags=_t, summary=_s.READ_ALL)
async def read_all(user: BasicUser) -> List[HistoryPublic]:
    if is_admin(user):
        return _hist.read_all()
    else:
        return user.history_created


@router.get(prefix(id=True), tags=_t, summary=_s.READ)
async def read(user: BasicUser, id: int) -> HistoryPublic:
    if is_admin(user):
        return _hist.read(id)
    else:
        return _hist.read_personal(id, user.history_created)


@router.put(prefix(id=True), tags=_t, summary=_s.UPDATE)
async def update(user: BasicUser, id: int,
                 hist: HistoryUpdate) -> Result:
    if is_admin(user):
        _hist.read(id)
        if hist.team_id is not None:
            _team.read(hist.team_id)
        if hist.player_id is not None:
            _player.read(hist.player_id)
    else:
        if hist.team_id is not None:
            _team.read_personal(hist.team_id, user.teams_created)
        if hist.player_id is not None:
            _player.read_personal(hist.player_id, user.players_created)
        _hist.read_personal(id, user.history_created)
    return _hist.update(id, hist, user)


@router.delete(prefix(id=True), tags=_t, summary=_s.DELETE)
async def delete(user: BasicUser, id: int) -> Result:
    if is_admin(user):
        _hist.read(id)
    else:
        _hist.read_personal(id, user.history_created)
    return _hist.delete(id)
