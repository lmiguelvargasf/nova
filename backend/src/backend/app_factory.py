from collections.abc import Awaitable, Callable

from litestar import Litestar, asgi, get
from litestar.types import Receive, Scope, Send
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


def _create_admin_handler():
    from .config.base import settings
    from .sqladmin_app import starlette_app as sqladmin_starlette_app

    @asgi("/admin/", is_mount=True, copy_scope=False)
    async def admin(scope: Scope, receive: Receive, send: Send) -> None:
        if not settings.admin_session_secret:
            await send(
                {
                    "type": "http.response.start",
                    "status": 503,
                    "headers": [(b"content-type", b"text/plain; charset=utf-8")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b"Admin session secret not configured.",
                }
            )
            return

        # Adjust scope so SQLAdmin (Starlette) sees paths relative to this mount.
        scope_path = scope.get("path", "")
        prefix = "/admin"
        if scope_path.startswith(prefix):
            new_scope = dict(scope)
            new_scope["root_path"] = (scope.get("root_path", "") or "") + prefix
            trimmed = scope_path[len(prefix) :]
            new_scope["path"] = trimmed if trimmed else "/"
            scope = new_scope  # type: ignore[assignment]

        await sqladmin_starlette_app(scope, receive, send)  # type: ignore[arg-type]

    return admin


def create_app(
    *,
    graphql_context_getter: Callable[[], Awaitable[dict[str, object]]]
    | Callable[[AsyncSession], Awaitable[dict[str, object]]]
    | None = None,
    include_admin: bool = True,
    use_sqlalchemy_plugin: bool = True,
) -> Litestar:
    if graphql_context_getter is None:
        graphql_context_getter = default_graphql_context_getter

    route_handlers = [
        health_check,
        create_graphql_controller(context_getter=graphql_context_getter),
    ]

    if include_admin:
        route_handlers.insert(0, _create_admin_handler())

    plugins = []
    if use_sqlalchemy_plugin:
        from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin

        from .config.alchemy import alchemy_config

        plugins.append(SQLAlchemyPlugin(config=alchemy_config))

    return Litestar(route_handlers=route_handlers, plugins=plugins)
