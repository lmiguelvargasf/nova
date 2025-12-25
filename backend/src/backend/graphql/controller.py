from collections.abc import Awaitable, Callable

from litestar import Request
from litestar.exceptions import NotAuthorizedException
from litestar.security.jwt import Token
from litestar.types import ControllerRouterHandler
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.litestar import make_graphql_controller

from backend.config.base import settings

from .context import GraphQLContext, Services
from .schema import schema

type GraphQLContextGetter = Callable[..., Awaitable[GraphQLContext]]


async def default_graphql_context_getter(
    db_session: AsyncSession,
    request: Request,
) -> GraphQLContext:
    services = Services(db_session)
    user = None

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token_str = auth_header.split(" ")[1]
        try:
            token = Token.decode(
                encoded_token=token_str,
                secret=settings.jwt_secret,
                algorithm="HS256",
            )
            user_id = token.sub
            if user_id:
                user = await services.users.get_one_or_none(id=int(user_id))
        except (NotAuthorizedException, ValueError):
            pass

    return GraphQLContext(
        db_session=db_session,
        services=services,
        user=user,
        request=request,
    )


def create_graphql_controller(
    *,
    context_getter: GraphQLContextGetter | None = None,
) -> ControllerRouterHandler:
    context_getter = context_getter or default_graphql_context_getter
    return make_graphql_controller(
        schema=schema,
        path="/graphql",
        context_getter=context_getter,
    )
