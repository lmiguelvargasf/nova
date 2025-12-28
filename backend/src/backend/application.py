from advanced_alchemy.extensions.litestar import SQLAlchemyAsyncConfig
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.plugins import PluginProtocol
from litestar.stores.memory import MemoryStore
from litestar.types import ControllerRouterHandler
from sqlalchemy.ext.asyncio import AsyncEngine

from .apps.users.rest import AuthController, UserController
from .auth.jwt import jwt_auth
from .config.base import settings
from .graphql.controller import (
    GraphQLContextGetter,
    create_graphql_controller,
)
from .health import health_check
from .middleware.rate_limit import get_rate_limit_middlewares


def create_app(
    *,
    graphql_context_getter: GraphQLContextGetter | None = None,
    use_sqlalchemy_plugin: bool = True,
    enable_admin: bool = True,
    admin_engine: AsyncEngine | None = None,
    alchemy_config_override: SQLAlchemyAsyncConfig | None = None,
) -> Litestar:
    cors_config = CORSConfig(allow_origins=settings.cors_allow_origins)
    route_handlers: list[ControllerRouterHandler] = [
        health_check,
        create_graphql_controller(context_getter=graphql_context_getter),
        AuthController,
        UserController,
    ]

    plugins: list[PluginProtocol] = []
    if use_sqlalchemy_plugin:
        from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin

        from .config.alchemy import alchemy_config as default_alchemy_config

        config = alchemy_config_override or default_alchemy_config
        plugins.append(SQLAlchemyPlugin(config=config))

    if enable_admin:
        from .admin.app import create_admin_handler

        route_handlers.append(create_admin_handler(engine=admin_engine))

    return Litestar(
        route_handlers=route_handlers,
        plugins=plugins,
        cors_config=cors_config,
        middleware=[
            *get_rate_limit_middlewares(),
        ],
        stores={"rate_limit": MemoryStore()},
        on_app_init=[jwt_auth.on_app_init],
    )
