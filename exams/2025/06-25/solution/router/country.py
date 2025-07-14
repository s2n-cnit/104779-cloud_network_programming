from enum import Enum
from typing import List

from db import DB
from error import NotEmptyException
from fastapi import APIRouter
from model import Country, CountryCreate, CountryPublic, CountryUpdate, Result
from router.lib import BasicUser, prefix

LABEL = "Country"
_t = [LABEL]
_pr = DB[Country](Country, LABEL)
router = APIRouter(prefix=f"/{LABEL.lower()}", tags=_t)


class _s(str, Enum):
    CREATE = "Insert a new country"
    READ_ALL = "Get all the countries"
    READ = "Get the details of a country"
    UPDATE = "Update a country"
    DELETE = "Delete a country"


@router.post(prefix(), tags=_t, summary=_s.CREATE)
async def create(user: BasicUser, country: CountryCreate) -> Result:
    return _pr.create(country, user)


@router.get(prefix(), tags=_t, summary=_s.READ_ALL)
async def read_all(user: BasicUser) -> List[CountryPublic]:
    return _pr.read_all()


@router.get(prefix(id=True), tags=_t, summary=_s.READ)
async def read(user: BasicUser, id: int) -> CountryPublic:
    return _pr.read(id)


@router.put(prefix(id=True), tags=_t, summary=_s.UPDATE)
async def update(user: BasicUser, id: int, country: CountryUpdate) -> Result:
    _pr.read(id)
    return _pr.update(id, pr, user)


@router.delete(prefix(id=True), tags=_t, summary=_s.DELETE)
async def delete(user: BasicUser, id: int) -> Result:
    pr = _pr.read(id)
    if len(pr.players) > 0:
        raise NotEmptyException(LABEL, id)
    return _pr.delete(id)
