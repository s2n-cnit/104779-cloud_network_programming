from enum import Enum
from typing import List

from db import DB
from error import NotEmptyException
from fastapi import APIRouter
from model import Result, Team, TeamUpdate, TeamCreate, TeamPublic
from router.lib import BasicUser, is_admin, prefix

LABEL = "Team"
_t = [LABEL]
_team = DB[Team](Team, LABEL)
router = APIRouter(prefix=f"/{LABEL.lower()}", tags=_t)


class _s(str, Enum):
    CREATE = "Insert a new team"
    READ_ALL = "Get all the teams"
    READ = "Get the details of a team"
    UPDATE = "Update a team"
    DELETE = "Delete a team"


@router.post(prefix(), tags=_t, summary=_s.CREATE)
async def create(user: BasicUser, team: TeamCreate) -> Result:
    return _team.create(team, user)


@router.get(prefix(), tags=_t, summary=_s.READ_ALL)
async def read_all(user: BasicUser) -> List[TeamPublic]:
    if is_admin(user):
        return _team.read_all()
    else:
        return user.teams_created


@router.get(prefix(id=True), tags=_t, summary=_s.READ)
async def read(user: BasicUser, id: int) -> TeamPublic:
    if is_admin(user):
        return _team.read(id)
    else:
        return _team.read_personal(id, user.teams_created)


@router.put(prefix(id=True), tags=_t, summary=_s.UPDATE)
async def update(
    user: BasicUser, id: int, team: TeamUpdate
) -> Result:
    if is_admin(user):
        _team.read(id)
    else:
        _team.read_personal(id, user.teams_created)
    return _team.update(id, team, user)


@router.delete(prefix(id=True), tags=_t, summary=_s.DELETE)
async def delete(user: BasicUser, id: int) -> Result:
    if is_admin(user):
        team = _team.read(id)
    else:
        team = _team.read_personal(id, user.teams_created)
    if len(team.history) > 0:
        raise NotEmptyException(LABEL, id)
    return _team.delete(id)
