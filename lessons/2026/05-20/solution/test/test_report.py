from functools import partial
from test.lib import ADD_FIELD
from test.lib import DATA_REPORT as DATA
from test.lib import FIELD_REPORT as FIELD
from test.lib import ID_NOT_FOUND
from test.lib import LABEL_REPORT as LABEL
from test.lib import ORDER_REPORT as ORDER
from test.lib import REF_REPORT as REF
from test.lib import RENAME_REPORT as RENAME
from test.lib import TARGET_REPORT as TARGET
from test.lib import UPDATE_REPORT as UPDATE
from test.lib import TestBase, _c, _d
from test.lib import _j as tmp_j
from test.lib import _r, _u, get_properties
from typing import Self

import pytest
from db import Action
from model import ReportPublic

_j = partial(tmp_j, LABEL)


@pytest.mark.parametrize(
    "username,password", [("admin", "admin"), ("alexcarrega", "test-me")]
)
class TestReport(TestBase):
    @pytest.mark.order(ORDER.create)
    def test_create(self: Self, username: str, auth_header: str) -> None:
        resp = _c(_j(), headers=auth_header, json=DATA)
        self.is_status_200(resp, Action.CREATED)
        self.save_id(username, REF, resp)

    @pytest.mark.order(ORDER.create)
    def test_create_wrong_field(self: Self, username: str,
                                auth_header: str) -> None:
        d = DATA.copy()
        d.rename(**RENAME)
        resp = _c(_j(), headers=auth_header, json=d)
        self.is_status_422(resp)

    @pytest.mark.order(ORDER.create)
    def test_create_miss_field(self: Self, username: str,
                               auth_header: str) -> None:
        d = DATA.copy()
        d.pop(FIELD)
        resp = _c(_j(), headers=auth_header, json=d)
        self.is_status_422(resp)

    @pytest.mark.order(ORDER.create)
    def test_create_add_field(self: Self, username: str,
                              auth_header: str) -> None:
        d = DATA.copy()
        d.update(**ADD_FIELD)
        resp = _c(_j(), headers=auth_header, json=d)
        self.is_status_200(resp, Action.CREATED)
        self.save_id(username, REF, resp)

    @pytest.mark.order(ORDER.read)
    def test_read(self: Self, username: str, auth_header: str) -> None:
        _id = self.get_id(username, REF, string=True)
        resp = _r(_j(_id), headers=auth_header)
        self.is_status_200(resp)
        json = resp.json()
        assert type(json) is dict
        for field in get_properties(ReportPublic):
            assert field in json

    @pytest.mark.order(ORDER.read)
    def test_read_all(self: Self, username: str, auth_header: str) -> None:
        resp = _r(_j(), headers=auth_header)
        self.is_status_200(resp)
        json = resp.json()
        assert type(json) is list, json
        assert len(json) > 0, json
        for field in get_properties(ReportPublic):
            assert field in json[0], (json, field)

    @pytest.mark.order(ORDER.read)
    def test_read_404(self: Self, username: str, auth_header: str) -> None:
        resp = _r(_j(str(ID_NOT_FOUND)), headers=auth_header)
        self.is_status_404(resp, TARGET)

    @pytest.mark.order(ORDER.update)
    def test_update(self: Self, username: str, auth_header: str) -> None:
        d = DATA.copy()
        d.update(**UPDATE)
        _id = self.get_id(username, REF, string=True)
        resp = _u(_j(_id), headers=auth_header, json=d)
        self.is_status_200(resp, Action.UPDATED)

    @pytest.mark.order(ORDER.update)
    def test_update_404(self: Self, username: str, auth_header: str) -> None:
        d = DATA.copy()
        d.update(**UPDATE)
        resp = _u(_j(str(ID_NOT_FOUND)), headers=auth_header, json=d)
        self.is_status_404(resp, TARGET)

    @pytest.mark.order(ORDER.update)
    def test_update_wrong_field(self: Self, username: str,
                                auth_header: str) -> None:
        d = DATA.copy()
        d.rename(**RENAME)
        _id = self.get_id(username, REF, string=True)
        resp = _u(_j(_id), headers=auth_header, json=d)
        self.is_status_200(resp, Action.UPDATED)

    @pytest.mark.order(ORDER.update)
    def test_update_add_field(self: Self, username: str,
                              auth_header: str) -> None:
        d = ADD_FIELD
        _id = self.get_id(username, REF, string=True)
        resp = _u(_j(_id), headers=auth_header, json=d)
        self.is_status_200(resp, Action.UPDATED)

    @pytest.mark.order(ORDER.delete)
    def test_del(self: Self, username: str, auth_header: str) -> None:
        _id = self.get_id(username, REF, string=True, delete=True, nth=1)
        resp = _d(_j(_id), headers=auth_header)
        self.is_status_200(resp, Action.DELETED)

    @pytest.mark.order(ORDER.delete)
    def test_del_not_empty(
        self: Self, username: str, auth_header: str
    ) -> None:
        _id = self.get_id(username, REF, string=True)
        resp = _d(_j(_id), headers=auth_header)
        self.is_status_406not_empty(resp, TARGET)

    @pytest.mark.order(ORDER.delete)
    def test_del_404(self: Self, username: str, auth_header: str) -> None:
        resp = _d(_j(str(ID_NOT_FOUND)), headers=auth_header)
        self.is_status_404(resp, TARGET)

    @pytest.mark.order(ORDER.delete_check)
    def test_del_check(self: Self, username: str, auth_header: str) -> None:
        _id = self.get_id(username, REF, string=True, delete=True)
        resp = _d(_j(_id), headers=auth_header)
        self.is_status_200(resp, Action.DELETED)
