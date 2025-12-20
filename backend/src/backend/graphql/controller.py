from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypedDict

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.litestar import make_graphql_controller

from ..apps.users.services import UserService
from ..schema import schema


class BackendGraphQLContext(TypedDict):
    db_session: AsyncSession
    user_service: UserService


async def default_graphql_context_getter(
    db_session: AsyncSession,
) -> BackendGraphQLContext:
    return {"db_session": db_session, "user_service": UserService(db_session)}


def create_graphql_controller(
    *,
    context_getter: Callable[[], Awaitable[dict[str, object] | BackendGraphQLContext]]
    | Callable[[AsyncSession], Awaitable[dict[str, object] | BackendGraphQLContext]],
):
    return make_graphql_controller(
        schema=schema,
        path="/graphql",
        context_getter=context_getter,
    )
