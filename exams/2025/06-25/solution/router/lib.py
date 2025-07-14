from typing import Annotated

from fastapi import Depends
from model import User
from router.auth import RoleChecker

AdminUser = Annotated[User, Depends(RoleChecker(allowed_role_ids=["admin"]))]

BasicUser = Annotated[
    User, Depends(RoleChecker(allowed_role_ids=["admin", "user"]))
]


def prefix(
    id: bool = False,
    me: bool = False,
    add_ex: bool = False,
    rm_ex: bool = False,
):
    return (
        ("/{id}" if id else "")
        + ("/me" if me else "")
        + ("/add" if add_ex else "")
        + ("/rm/{exercise_id}" if rm_ex else "")
    )


def is_admin(user: User):
    return user.role_id == "admin"
