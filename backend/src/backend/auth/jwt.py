from advanced_alchemy.extensions.litestar import SQLAlchemyAsyncConfig
from litestar.connection import ASGIConnection
from litestar.security.jwt import JWTAuth, Token

from backend.apps.users.models import UserModel
from backend.apps.users.services import UserService
from backend.config.base import settings


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection
) -> UserModel | None:
    config = connection.app.state.get("alchemy_config")
    if not isinstance(config, SQLAlchemyAsyncConfig):
        return None

    try:
        user_id = int(token.sub)
    except TypeError, ValueError:
        return None

    async with config.get_session() as session:
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
