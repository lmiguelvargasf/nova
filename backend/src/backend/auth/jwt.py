from litestar.connection import ASGIConnection
from litestar.security.jwt import JWTAuth, Token
from sqlalchemy.ext.asyncio import AsyncSession

from backend.apps.users.models import UserModel
from backend.apps.users.services import UserService
from backend.config.base import settings


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection
) -> UserModel | None:
    session = getattr(connection.state, "db_session", None)
    if not isinstance(session, AsyncSession):
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
