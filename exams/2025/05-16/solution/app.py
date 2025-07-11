import router
from config import app_name, debug, logger  # noqa: F401
from error import (ConflictException, EmptyException,
                   InternalServerErrorException, NotAcceptableException,
                   NotEmptyException, NotFoundException, exception_handler)
from fastapi import FastAPI

app = FastAPI(title=app_name, debug=debug)

app.include_router(router.auth)
app.include_router(router.player_role)
app.include_router(router.team)
app.include_router(router.player)
app.include_router(router.history)
app.include_router(router.user)

app.add_exception_handler(ConflictException, exception_handler)
app.add_exception_handler(EmptyException, exception_handler)
app.add_exception_handler(NotEmptyException, exception_handler)
app.add_exception_handler(InternalServerErrorException, exception_handler)
app.add_exception_handler(NotAcceptableException, exception_handler)
app.add_exception_handler(NotFoundException, exception_handler)
