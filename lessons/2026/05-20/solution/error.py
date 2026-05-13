from datetime import datetime
from enum import Enum
from typing import Optional, Self

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class Action(str, Enum):
    NOT_FOUND = "Not Found"
    CONFLICT = "Conflict"
    EMPTY = "Empty"
    NOT_EMPTY = "Not Empty"
    NOT_ACCEPTABLE = "Not Acceptable"
    INTERNAL_SERVER_ERROR = "Internal Server Error"


class BaseException(Exception):
    def __init__(self: Self,
                 target: str,
                 id: Optional[str | int] = None,
                 detail: Optional[str] = None) -> Self:
        self.target = target
        self.id = id
        self.detail = detail

    def response(self: Self) -> JSONResponse:
        c = dict(
            action=self.action,
            target=self.target,
            error=True,
            success=False,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
        )
        if self.id:
            c.update(id=self.id)
        if self.detail:
            c.update(detail=self.detail)
        return JSONResponse(
            status_code=self.status,
            content=jsonable_encoder(c),
        )


async def exception_handler(
    request: Request, exc: BaseException
) -> JSONResponse:
    return exc.response()


class NotFoundException(BaseException):
    action = Action.NOT_FOUND
    status = status.HTTP_404_NOT_FOUND


class ConflictException(BaseException):
    action = Action.CONFLICT
    status = status.HTTP_409_CONFLICT


class EmptyException(BaseException):
    action = Action.EMPTY
    status = status.HTTP_406_NOT_ACCEPTABLE


class NotEmptyException(BaseException):
    action = Action.NOT_EMPTY
    status = status.HTTP_406_NOT_ACCEPTABLE


class NotAcceptableException(BaseException):
    action = Action.NOT_ACCEPTABLE
    status = status.HTTP_406_NOT_ACCEPTABLE


class InternalServerErrorException(BaseException):
    action = Action.INTERNAL_SERVER_ERROR
    status = status.HTTP_500_INTERNAL_SERVER_ERROR
