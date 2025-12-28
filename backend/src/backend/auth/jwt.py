from collections.abc import Callable
from typing import cast

from advanced_alchemy._listeners import set_async_context
from advanced_alchemy.extensions.litestar import SQLAlchemyInitPlugin
from advanced_alchemy.extensions.litestar._utils import (
    get_aa_scope_state,
    set_aa_scope_state,
)
from advanced_alchemy.extensions.litestar.plugins.init.config.common import (
    SESSION_SCOPE_KEY,
)
from litestar.connection import ASGIConnection
from litestar.security.jwt import JWTAuth, Token
from sqlalchemy.ext.asyncio import AsyncSession

from backend.apps.users.models import UserModel
from backend.apps.users.services import UserService
from backend.config.base import settings


def _get_session_maker(
    connection: ASGIConnection,
) -> Callable[[], AsyncSession] | None:
    try:
        plugin = connection.app.plugins.get(SQLAlchemyInitPlugin)
    except KeyError:
        plugin = None

    if plugin is not None:
        for config in plugin.config:
            session_maker = connection.app.state.get(config.session_maker_app_state_key)
            if callable(session_maker):
                return cast("Callable[[], AsyncSession]", session_maker)

    session_maker = connection.app.state.get("session_maker_class")
    if callable(session_maker):
        return cast("Callable[[], AsyncSession]", session_maker)
    return None


def _get_session_scope_key(connection: ASGIConnection) -> str:
    try:
        plugin = connection.app.plugins.get(SQLAlchemyInitPlugin)
    except KeyError:
        return SESSION_SCOPE_KEY

    for config in plugin.config:
        if config.session_scope_key:
            return config.session_scope_key

    return SESSION_SCOPE_KEY


def _get_db_session(connection: ASGIConnection) -> AsyncSession | None:
    session_scope_key = _get_session_scope_key(connection)
    session = get_aa_scope_state(connection.scope, session_scope_key)
    if isinstance(session, AsyncSession):
        return session

    session_maker = _get_session_maker(connection)
    if not callable(session_maker):
        return None

    session = session_maker()
    set_aa_scope_state(connection.scope, session_scope_key, session)
    set_async_context(True)
    return session


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection
) -> UserModel | None:
    session = _get_db_session(connection)
    if session is None:
        return None

    try:
        user_id = int(token.sub)
    except (TypeError, ValueError):
        return None

    return await UserService(session).get_one_or_none(id=user_id)


jwt_auth = JWTAuth[UserModel](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=settings.jwt_secret,
    exclude=[
        "/graphql",
        "/schema",
        "/health",
        "/admin",
        "/api/auth/login",
        "/api/auth/register",
    ],
)
