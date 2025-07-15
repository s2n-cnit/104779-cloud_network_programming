from enum import Enum
from typing import List

from db import DB
from error import NotEmptyException
from fastapi import APIRouter
from model import City, Result, CityUpdate, CityCreate, CityPublic
from router.country import _country
from router.lib import BasicUser, is_admin, prefix

LABEL = "City"
_t = [LABEL]
_city = DB[City](City, LABEL)
router = APIRouter(prefix=f"/{LABEL.lower()}", tags=_t)


class _s(str, Enum):
    CREATE = "Insert a new city"
    READ_ALL = "Get all the cities"
    READ = "Get the details of a city"
    UPDATE = "Update a city"
    DELETE = "Delete a city"


@router.post(prefix(), tags=_t, summary=_s.CREATE)
async def create(user: BasicUser, city: CityCreate) -> Result:
    _country.read(city.country_id)
    return _city.create(city, user)


@router.get(prefix(), tags=_t, summary=_s.READ_ALL)
async def read_all(user: BasicUser) -> List[CityPublic]:
    if is_admin(user):
        return _city.read_all()
    else:
        return user.cities_created


@router.get(prefix(id=True), tags=_t, summary=_s.READ)
async def read(user: BasicUser, id: int) -> CityPublic:
    if is_admin(user):
        return _city.read(id)
    else:
        return _city.read_personal(id, user.cities_created)


@router.put(prefix(id=True), tags=_t, summary=_s.UPDATE)
async def update(user: BasicUser, id: int, city: CityUpdate) -> Result:
    if is_admin(user):
        _city.read(id)
    else:
        _city.read_personal(id, user.cities_created)
    if city.country_id is not None:
        _country.read(city.country_id)
    return _city.update(id, city, user)


@router.delete(prefix(id=True), tags=_t, summary=_s.DELETE)
async def delete(user: BasicUser, id: int) -> Result:
    if is_admin(user):
        city = _city.read(id)
    else:
        city = _city.read_personal(id, user.cities_created)
    if len(city.report_history) > 0:
        raise NotEmptyException(LABEL, id)
    return _city.delete(id)
