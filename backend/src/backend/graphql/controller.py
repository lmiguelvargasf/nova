from collections.abc import Awaitable, Callable
from typing import TypedDict

from litestar import Request
from litestar.types import ControllerRouterHandler
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.litestar import make_graphql_controller

from backend.apps.users.models import UserModel
from backend.apps.users.services import UserService

from .schema import schema


class GraphQLContext(TypedDict):
    db_session: AsyncSession
    user_service: UserService
    current_user: UserModel | None


type GraphQLContextGetter = Callable[..., Awaitable[GraphQLContext]]


async def default_graphql_context_getter(
    request: Request,
    db_session: AsyncSession,
) -> GraphQLContext:
    return {
        "db_session": db_session,
        "user_service": UserService(db_session),
        "current_user": request.scope.get("user"),
    }


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
