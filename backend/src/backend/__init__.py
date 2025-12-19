from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin
from litestar import Litestar, asgi, get
from litestar.types import Receive, Scope, Send
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.litestar import make_graphql_controller

from .config.alchemy import alchemy_config
from .config.base import settings
from .schema import schema
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


class HealthStatus(BaseModel):
    status: str


@get("/health")
async def health_check() -> HealthStatus:
    return HealthStatus(status="ok")


async def graphql_context_getter(db_session: AsyncSession) -> dict[str, object]:
    return {"db_session": db_session}


GraphQLController = make_graphql_controller(
    schema=schema,
    path="/graphql",
    context_getter=graphql_context_getter,
)

app = Litestar(
    route_handlers=[admin, health_check, GraphQLController],
    plugins=[SQLAlchemyPlugin(config=alchemy_config)],
)
