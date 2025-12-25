from litestar.connection import ASGIConnection
from litestar.security.jwt import JWTAuth, Token
from sqlalchemy.ext.asyncio import AsyncSession

from backend.apps.users.models import UserModel
from backend.apps.users.services import UserService
from backend.config.base import settings


def _get_db_session(connection: ASGIConnection) -> AsyncSession | None:
    """Helper to safely retrieve the database session from connection state."""
    session = getattr(connection.state, "db_session", None) or getattr(
        connection.state, "session", None
    )
    if isinstance(session, AsyncSession):
        return session
    return None


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
    exclude=["/graphql", "/schema", "/health", "/admin"],
)
