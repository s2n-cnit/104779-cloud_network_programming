from enum import Enum
from typing import List

from db import DB
from fastapi import APIRouter
from model import (ReportHistory, ReportHistoryCreate,
                   ReportHistoryPublic, ReportHistoryUpdate, Result)
from router.city import _city
from router.lib import BasicUser, is_admin, prefix
from router.report import _report

LABEL = "Report History"

_t = [LABEL]
_rep_hist = DB[ReportHistory](ReportHistory, LABEL)
router = APIRouter(prefix=f"/report-history", tags=_t)


class _s(str, Enum):
    CREATE = "Insert a new record in the report history"
    READ = "Get the details of the report history"
    READ_ALL = "Get the details of the report history of all the cities"
    UPDATE = "Update the data about the record of the report history of a city"
    DELETE = "Delete a record from the report history of a city"


@router.post(prefix(), tags=_t, summary=_s.CREATE)
async def create(user: BasicUser, rep_hist: ReportHistoryCreate) -> Result:
    if is_admin(user):
        _city.read(rep_hist.city_id)
        _report.read(rep_hist.report_id)
    else:
        _city.read_personal(rep_hist.city_id, user.cities_created)
        _report.read_personal(rep_hist.report_id, user.reports_created)
    return _rep_hist.create(rep_hist, user)


@router.get(prefix(), tags=_t, summary=_s.READ_ALL)
async def read_all(user: BasicUser) -> List[ReportHistoryPublic]:
    if is_admin(user):
        return _rep_hist.read_all()
    else:
        return user.report_history_created


@router.get(prefix(id=True), tags=_t, summary=_s.READ)
async def read(user: BasicUser, id: int) -> ReportHistoryPublic:
    if is_admin(user):
        return _rep_hist.read(id)
    else:
        return _rep_hist.read_personal(id, user.report_history_created)


@router.put(prefix(id=True), tags=_t, summary=_s.UPDATE)
async def update(user: BasicUser, id: int,
                 rep_hist: ReportHistoryUpdate) -> Result:
    rep_hist_saved = _rep_hist.read(id)
    if is_admin(user):
        if rep_hist_saved.report_id is not None:
            _report.read(rep_hist_saved.report_id)
        if rep_hist_saved.city_id is not None:
            _city.read(rep_hist_saved.city_id)
    else:
        if rep_hist_saved.report_id is not None:
            _report.read_personal(rep_hist_saved.report_id, user.reports_created)
        if rep_hist_saved.city_id is not None:
            _city.read_personal(rep_hist_saved.city_id, user.cities_created)
    return _rep_hist.update(id, rep_hist, user)


@router.delete(prefix(id=True), tags=_t, summary=_s.DELETE)
async def delete(user: BasicUser, id: int) -> Result:
    if is_admin(user):
        _rep_hist.read(id)
    else:
        _rep_hist.read_personal(id, user.report_history_created)
    return _rep_hist.delete(id)
