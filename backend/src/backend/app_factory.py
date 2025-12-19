from collections.abc import Awaitable, Callable

from litestar import Litestar, get
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.litestar import make_graphql_controller

from .apps.users.services import UserService
from .schema import schema


async def default_graphql_context_getter(
    db_session: AsyncSession,
) -> dict[str, object]:
    return {"db_session": db_session, "user_service": UserService(db_session)}


def create_graphql_controller(
    *,
    context_getter: Callable[[], Awaitable[dict[str, object]]]
    | Callable[[AsyncSession], Awaitable[dict[str, object]]],
):
    return make_graphql_controller(
        schema=schema,
        path="/graphql",
        context_getter=context_getter,
    )


class HealthStatus(BaseModel):
    status: str


@get("/health")
async def health_check() -> HealthStatus:
    return HealthStatus(status="ok")


def create_app(
    *,
    graphql_context_getter: Callable[[], Awaitable[dict[str, object]]]
    | Callable[[AsyncSession], Awaitable[dict[str, object]]]
    | None = None,
    use_sqlalchemy_plugin: bool = True,
) -> Litestar:
    if graphql_context_getter is None:
        graphql_context_getter = default_graphql_context_getter

    route_handlers = [
        health_check,
        create_graphql_controller(context_getter=graphql_context_getter),
    ]

    plugins = []
    if use_sqlalchemy_plugin:
        from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin

        from .config.alchemy import alchemy_config

        plugins.append(SQLAlchemyPlugin(config=alchemy_config))

    return Litestar(route_handlers=route_handlers, plugins=plugins)
