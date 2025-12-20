from collections.abc import Awaitable, Callable

from litestar import Litestar
from sqlalchemy.ext.asyncio import AsyncSession

from .graphql.controller import (
    BackendGraphQLContext,
    create_graphql_controller,
    default_graphql_context_getter,
)
from .health import health_check


def create_app(
    *,
    graphql_context_getter: Callable[
        [], Awaitable[dict[str, object] | BackendGraphQLContext]
    ]
    | Callable[[AsyncSession], Awaitable[dict[str, object] | BackendGraphQLContext]]
    | None = None,
    use_sqlalchemy_plugin: bool = True,
) -> Litestar:
    if graphql_context_getter is None:
        context_getter = default_graphql_context_getter
    else:
        context_getter = graphql_context_getter

    route_handlers = [
        health_check,
        create_graphql_controller(context_getter=context_getter),
    ]

    plugins = []
    if use_sqlalchemy_plugin:
        from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin

        from .config.alchemy import alchemy_config

        plugins.append(SQLAlchemyPlugin(config=alchemy_config))

    return Litestar(route_handlers=route_handlers, plugins=plugins)
