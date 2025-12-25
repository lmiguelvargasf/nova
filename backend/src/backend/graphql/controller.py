from collections.abc import Awaitable, Callable

from litestar import Request
from litestar.types import ControllerRouterHandler
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.litestar import make_graphql_controller

from .context import GraphQLContext, Services
from .schema import schema

type GraphQLContextGetter = Callable[..., Awaitable[GraphQLContext]]


async def default_graphql_context_getter(
    request: Request,
    db_session: AsyncSession,
) -> GraphQLContext:
    return GraphQLContext(db_session=db_session, services=Services(db_session))


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
