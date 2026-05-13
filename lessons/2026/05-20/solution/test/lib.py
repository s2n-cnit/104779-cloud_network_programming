import time
from datetime import datetime
from typing import List, Optional, Self, Type

import pytest
from app import app
from db import Action
from error import Action as ActionError
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response
from sqlmodel import SQLModel
from utils import ImmutableDict, Struct

__client = TestClient(app)

_c = __client.post
_r = __client.get
_u = __client.put
_d = __client.delete

ID_NOT_FOUND = 0
ADD_FIELD = ImmutableDict(add_field="test")
SLEEP_SECONDS = 0


def get_properties(ref: Type[SQLModel]) -> List[str]:
    return list(ref.model_json_schema()["properties"].keys())


def _j(*args, sep="/") -> str:
    return sep.join(args)


UPDATE_CITY = ImmutableDict(name="new-city-name", latitude=11.3, longitude=31.5)
UPDATE_COUNTRY = ImmutableDict(name="new-country-name")
UPDATE_REPORT = ImmutableDict(name="new-report-name", unit="new-unit", description="new-description")
_start_date = datetime(2020, 9, 20, 10, 30, 00).isoformat()
_end_date = datetime(2022, 7, 1, 10, 30, 00).isoformat()
UPDATE_REPORT_HISTORY = ImmutableDict(start_date=_start_date, end_date=_end_date, measure=40.3)

DATA_COUNTRY = ImmutableDict(name="country-name")
DATA_CITY = ImmutableDict(name="city-name", latitude=10.3, longitude=34.5)
DATA_REPORT = ImmutableDict(name="report-name", unit="report-unit", description="report-description")
_start_date = datetime(2021, 9, 21, 10, 30, 00).isoformat()
_end_date = datetime(2023, 7, 10, 10, 30, 00).isoformat()
DATA_REPORT_HISTORY = ImmutableDict(start_date=_start_date, end_date=_end_date, measure=10.3)

ORDER_COUNTRY = Struct(create=1, read=2, update=3, delete=88, delete_check=100)
ORDER_CITY = Struct(create=11, read=12, update=13, delete=89, delete_check=95)
ORDER_REPORT = Struct(
    create=21, read=22, update=23, delete=89, delete_check=95
)
ORDER_REPORT_HISTORY = Struct(create=31, read=32, update=33, delete=90)

FIELD_COUNTRY = "name"
FIELD_CITY = "name"
FIELD_REPORT = "unit"
FIELD_REPORT_HISTORY = "start_date"

RENAME_COUNTRY = ImmutableDict(name="names")
RENAME_CITY = ImmutableDict(name="names")
RENAME_REPORT = ImmutableDict(unit="units")
RENAME_REPORT_HISTORY = ImmutableDict(start_date="start_dates")

LABEL_COUNTRY = "country"
LABEL_CITY = "city"
LABEL_REPORT = "report"
LABEL_REPORT_HISTORY = "report-history"

TARGET_COUNTRY = "Country"
TARGET_CITY = "City"
TARGET_REPORT = "Report"
TARGET_REPORT_HISTORY = "Report History"

REF_COUNTRY = "country"
REF_CITY = "city"
REF_REPORT = "report"
REF_REPORT_HISTORY = "report-history"


class TestBase:
    def is_admin(self: Self, username: str) -> bool:
        return username == "admin"

    def is_admin_ok(self: Self, username: str, resp) -> bool:
        if not self.is_admin(username):
            assert (
                resp.status_code == status.HTTP_401_UNAUTHORIZED
            ), resp.json()
            return False
        return True

    def save_id(
        self: Self, username: str, target: str, resp: Response
    ) -> None:
        json = resp.json()
        _id = json["id"]
        for k in [username, "___"]:
            if target not in pytest.data[k]:
                pytest.data[k][target] = []
            pytest.data[k][target].append(_id)

    def get_id(
        self: Self,
        username: str,
        target: str,
        string: bool = False,
        personal: bool = True,
        delete: bool = False,
        nth: int = 0,
    ) -> int | str | List[str]:
        k = username if personal else "___"
        if target in pytest.data[k]:
            assert len(pytest.data[k][target]) > nth, len(
                pytest.data[k][target]
            )
            _x = pytest.data[k][target][nth]
            if delete:
                pytest.data[k][target].remove(_x)
            return str(_x) if string else _x
        else:
            return "0" if string else 0

    def is_status_200(
        self: Self, resp: Response, action: Optional[Action] = None
    ) -> None:
        assert resp.status_code == status.HTTP_200_OK, resp.json()
        assert resp.headers["Content-Type"] == "application/json", resp.json()
        if action is not None:
            json = resp.json()
            assert json["action"] == action, json

    def is_status_404(self: Self, resp: Response, target: str) -> None:
        assert resp.status_code == status.HTTP_404_NOT_FOUND, resp.json()
        assert resp.headers["Content-Type"] == "application/json", resp.json()
        json = resp.json()
        assert json["action"] == ActionError.NOT_FOUND, json
        assert json["error"] is True, json
        assert json["success"] is False, json
        assert json["target"] == target, json

    def is_status_422(self: Self, resp: Response) -> None:
        _s = status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.status_code == _s, resp.json()
        assert resp.headers["Content-Type"] == "application/json", resp.json()
        json = resp.json()
        assert json["detail"][0]["type"] == "missing", json

    def is_status_406(self: Self, resp: Response) -> None:
        assert resp.status_code == status.HTTP_406_NOT_ACCEPTABLE, resp.json()
        assert resp.headers["Content-Type"] == "application/json", resp.json()
        json = resp.json()
        assert "detail" in json, json

    def is_status_406not_empty(
        self: Self, resp: Response, target: str
    ) -> None:
        assert resp.status_code == status.HTTP_406_NOT_ACCEPTABLE, resp.json()
        assert resp.headers["Content-Type"] == "application/json", resp.json()
        json = resp.json()
        assert "action" in json, json
        assert json["action"] == ActionError.NOT_EMPTY, json
        assert json["error"] is True, json
        assert json["success"] is False, json
        assert json["target"] == target, json

    def teardown_method(self, method):
        time.sleep(SLEEP_SECONDS)
