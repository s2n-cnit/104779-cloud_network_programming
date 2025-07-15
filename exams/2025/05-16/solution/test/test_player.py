from functools import partial
from test.lib import ADD_FIELD
from test.lib import DATA_PLAYER as DATA
from test.lib import FIELD_PLAYER as FIELD
from test.lib import ID_NOT_FOUND
from test.lib import LABEL_PLAYER as LABEL
from test.lib import ORDER_PLAYER as ORDER
from test.lib import REF_PLAYER_ROLE
from test.lib import REF_PLAYER as REF
from test.lib import RENAME_PLAYER as RENAME
from test.lib import TARGET_PLAYER_ROLE
from test.lib import TARGET_PLAYER as TARGET
from test.lib import UPDATE_PLAYER as UPDATE
from test.lib import TestBase, _c, _d
from test.lib import _j as tmp_j
from test.lib import _r, _u, get_properties
from typing import Self
import pytest
from db import Action
from model import PlayerPublic

_j = partial(tmp_j, LABEL)


@pytest.mark.parametrize(
    "username,password", [("admin", "admin"), ("alexcarrega", "test-me")]
)
class TestPlayer(TestBase):
    @pytest.mark.order(ORDER.create)
    def test_create(self: Self, username: str, auth_header: str) -> None:
        d = DATA.copy()
        d.update(player_role_id=self.get_id(username, REF_PLAYER_ROLE))
        resp = _c(_j(), headers=auth_header, json=d)
        self.is_status_200(resp, Action.CREATED)
        self.save_id(username, REF, resp)

    @pytest.mark.order(ORDER.create)
    def test_create_wrong_field(self: Self, username: str,
                                auth_header: str) -> None:
        d = DATA.copy()
        d.rename(**RENAME)
        d.update(player_role_id=self.get_id(username, REF_PLAYER_ROLE))
        resp = _c(_j(), headers=auth_header, json=d)
        self.is_status_422(resp)

    @pytest.mark.order(ORDER.create)
    def test_create_miss_field(self: Self, username: str,
                               auth_header: str) -> None:
        d = DATA.copy()
        d.pop(FIELD)
        d.update(player_role_id=self.get_id(username, REF_PLAYER_ROLE))
        resp = _c(_j(), headers=auth_header, json=d)
        self.is_status_422(resp)

    @pytest.mark.order(ORDER.create)
    def test_create_add_field(self: Self, username: str,
                              auth_header: str) -> None:
        d = DATA.copy()
        d.update(player_role_id=self.get_id(username, REF_PLAYER_ROLE))
        d.update(**ADD_FIELD)
        resp = _c(_j(), headers=auth_header, json=d)
        self.is_status_200(resp, Action.CREATED)
        self.save_id(username, REF, resp)

    @pytest.mark.order(ORDER.create)
    def test_create_404pr(self: Self, username: str,
                          auth_header: str) -> None:
        d = DATA.copy()
        d.update(player_role_id=ID_NOT_FOUND)
        resp = _c(_j(), headers=auth_header, json=d)
        self.is_status_404(resp, TARGET_PLAYER_ROLE)

    @pytest.mark.order(ORDER.create)
    def test_create_404pr_wrong_field(self: Self, username: str,
                                      auth_header: str) -> None:
        d = DATA.copy()
        d.rename(**RENAME)
        d.update(player_role_id=ID_NOT_FOUND)
        resp = _c(_j(), headers=auth_header, json=d)
        self.is_status_422(resp)

    @pytest.mark.order(ORDER.create)
    def test_create_404pr_miss_field(self: Self, username: str,
                                     auth_header: str) -> None:
        d = DATA.copy()
        d.pop(FIELD)
        d.update(player_role_id=ID_NOT_FOUND)
        resp = _c(_j(), headers=auth_header, json=d)
        self.is_status_422(resp)

    @pytest.mark.order(ORDER.create)
    def test_create_404pr_add_field(self: Self, username: str,
                                    auth_header: str) -> None:
        d = DATA.copy()
        d.update(player_role_id=ID_NOT_FOUND, **ADD_FIELD)
        resp = _c(_j(), headers=auth_header, json=d)
        self.is_status_404(resp, TARGET_PLAYER_ROLE)

    @pytest.mark.order(ORDER.read)
    def test_read(self: Self, username: str, auth_header: str) -> None:
        _id = self.get_id(username, REF, string=True)
        resp = _r(_j(_id), headers=auth_header)
        self.is_status_200(resp)
        json = resp.json()
        assert type(json) is dict, json
        for field in get_properties(PlayerPublic):
            assert field in json, (json, field)

    @pytest.mark.order(ORDER.read)
    def test_read_all(self: Self, username: str, auth_header: str) -> None:
        resp = _r(_j(), headers=auth_header)
        self.is_status_200(resp)
        json = resp.json()
        assert type(json) is list, json
        assert len(json) > 0, json
        for field in get_properties(PlayerPublic):
            assert field in json[0], (json, field)

    @pytest.mark.order(ORDER.read)
    def test_read_404(self: Self, username: str, auth_header: str) -> None:
        resp = _r(_j(str(ID_NOT_FOUND)), headers=auth_header)
        self.is_status_404(resp, TARGET)

    @pytest.mark.order(ORDER.update)
    def test_update(self: Self, username: str, auth_header: str) -> None:
        d = DATA.copy()
        pr_id = self.get_id(username, REF_PLAYER_ROLE)
        d.update(**UPDATE, player_role_id=pr_id)
        _id = self.get_id(username, REF, string=True)
        resp = _u(_j(_id), headers=auth_header, json=d)
        self.is_status_200(resp, Action.UPDATED)

    @pytest.mark.order(ORDER.update)
    def test_update_404(self: Self, username: str, auth_header: str) -> None:
        d = DATA.copy()
        pr_id = self.get_id(username, REF_PLAYER_ROLE)
        d.update(**UPDATE, player_role_id=pr_id)
        _id = str(ID_NOT_FOUND)
        resp = _u(_j(_id), headers=auth_header, json=d)
        self.is_status_404(resp, TARGET)

    @pytest.mark.order(ORDER.update)
    def test_update_wrong_field(self: Self, username: str,
                                auth_header: str) -> None:
        d = DATA.copy()
        d.rename(**RENAME)
        d.update(player_role_id=self.get_id(username, REF_PLAYER_ROLE))
        _id = self.get_id(username, REF, string=True)
        resp = _u(_j(_id), headers=auth_header, json=d)
        self.is_status_200(resp, Action.UPDATED)

    @pytest.mark.order(ORDER.update)
    def test_update_add_field(self: Self, username: str,
                              auth_header: str) -> None:
        _id = self.get_id(username, REF, string=True)
        resp = _u(_j(_id), headers=auth_header, json=ADD_FIELD)
        self.is_status_200(resp, Action.UPDATED)

    @pytest.mark.order(ORDER.update)
    def test_update_404pr(self: Self, username: str,
                          auth_header: str) -> None:
        d = DATA.copy()
        d.update(**UPDATE, player_role_id=ID_NOT_FOUND)
        _id = self.get_id(username, REF, string=True)
        res = _u(_j(_id), headers=auth_header, json=d)
        self.is_status_404(res, TARGET_PLAYER_ROLE)

    @pytest.mark.order(ORDER.update)
    def test_update_404pr_wrong_field(self: Self, username: str,
                                      auth_header: str) -> None:
        d = DATA.copy()
        d.rename(**RENAME)
        d.update(player_role_id=ID_NOT_FOUND)
        _id = self.get_id(username, REF, string=True)
        res = _u(_j(_id), headers=auth_header, json=d)
        self.is_status_404(res, TARGET_PLAYER_ROLE)

    @pytest.mark.order(ORDER.update)
    def test_update_404pr_add_field(self: Self, username: str,
                                    auth_header: str) -> None:
        d = DATA.copy()
        d.update(player_role_id=ID_NOT_FOUND, **ADD_FIELD)
        _id = self.get_id(username, REF, string=True)
        res = _u(_j(_id), headers=auth_header, json=d)
        self.is_status_404(res, TARGET_PLAYER_ROLE)

    @pytest.mark.order(ORDER.delete_check)
    def test_del(self: Self, username: str, auth_header: str) -> None:
        for _i in (0, 0):
            _id = self.get_id(username, REF, string=True, delete=True, nth=_i)
            resp = _d(_j(_id), headers=auth_header)
            self.is_status_200(resp, Action.DELETED)

    @pytest.mark.order(ORDER.delete)
    def test_del_not_empty(self: Self, username: str,
                           auth_header: str) -> None:
        for _i in (0, 1):
            _id = self.get_id(username, REF, string=True, nth=_i)
            resp = _d(_j(_id), headers=auth_header)
            self.is_status_406not_empty(resp, TARGET)

    @pytest.mark.order(ORDER.delete)
    def test_del_404(self: Self, username: str, auth_header: str) -> None:
        resp = _d(_j(str(ID_NOT_FOUND)), headers=auth_header)
        self.is_status_404(resp, TARGET)
