from collections.abc import Awaitable, Callable
from typing import TypedDict

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.litestar import make_graphql_controller

from ..apps.users.services import UserService
from .schema import schema


class GraphQLContext(TypedDict):
    db_session: AsyncSession
    user_service: UserService


type GraphQLContextGetter = (
    Callable[[], Awaitable[GraphQLContext]]
    | Callable[[AsyncSession], Awaitable[GraphQLContext]]
)


async def default_graphql_context_getter(
    db_session: AsyncSession,
) -> GraphQLContext:
    return {"db_session": db_session, "user_service": UserService(db_session)}


def create_graphql_controller(
    *,
    context_getter: GraphQLContextGetter | None = None,
):
    context_getter = context_getter or default_graphql_context_getter
    return make_graphql_controller(
        schema=schema,
        path="/graphql",
        context_getter=context_getter,
    )
