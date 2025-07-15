from enum import Enum
from typing import List

from db import DB
from error import NotEmptyException
from fastapi import APIRouter
from model import Result, Report, ReportUpdate, ReportCreate, ReportPublic
from router.lib import BasicUser, is_admin, prefix

LABEL = "Report"
_t = [LABEL]
_report = DB[Report](Report, LABEL)
router = APIRouter(prefix=f"/{LABEL.lower()}", tags=_t)


class _s(str, Enum):
    CREATE = "Insert a new report"
    READ_ALL = "Get all the reports"
    READ = "Get the details of a report"
    UPDATE = "Update a report"
    DELETE = "Delete a report"


@router.post(prefix(), tags=_t, summary=_s.CREATE)
async def create(user: BasicUser, report: ReportCreate) -> Result:
    return _report.create(report, user)


@router.get(prefix(), tags=_t, summary=_s.READ_ALL)
async def read_all(user: BasicUser) -> List[ReportPublic]:
    if is_admin(user):
        return _report.read_all()
    else:
        return user.reports_created


@router.get(prefix(id=True), tags=_t, summary=_s.READ)
async def read(user: BasicUser, id: int) -> ReportPublic:
    if is_admin(user):
        return _report.read(id)
    else:
        return _report.read_personal(id, user.reports_created)


@router.put(prefix(id=True), tags=_t, summary=_s.UPDATE)
async def update(
    user: BasicUser, id: int, report: ReportUpdate
) -> Result:
    if is_admin(user):
        _report.read(id)
    else:
        _report.read_personal(id, user.reports_created)
    return _report.update(id, report, user)


@router.delete(prefix(id=True), tags=_t, summary=_s.DELETE)
async def delete(user: BasicUser, id: int) -> Result:
    if is_admin(user):
        report = _report.read(id)
    else:
        report = _report.read_personal(id, user.reports_created)
    if len(report.report_history) > 0:
        raise NotEmptyException(LABEL, id)
    return _report.delete(id)
