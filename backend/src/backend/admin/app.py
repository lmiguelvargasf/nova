from pathlib import Path

from litestar import asgi
from litestar.handlers.asgi_handlers import ASGIRouteHandler
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.types import Receive, Scope, Send
from starlette_admin import BaseAdmin
from starlette_admin.contrib.sqla.middleware import DBSessionMiddleware

from backend.config.alchemy import alchemy_config

from .auth import BackendAdminAuthProvider
from .views import ADMIN_VIEWS


def create_admin_handler(
    *,
    engine: AsyncEngine | None = None,
) -> ASGIRouteHandler:
    """Create a Litestar ASGI handler that mounts the Starlette Admin app."""
    db_engine = engine or alchemy_config.get_engine()
    base_dir = Path(__file__).resolve().parent

    admin = BaseAdmin(
        title="Admin",
        auth_provider=BackendAdminAuthProvider(),
        templates_dir=str(base_dir / "templates"),
        statics_dir=str(base_dir / "statics"),
        middlewares=[
            Middleware(DBSessionMiddleware, engine=db_engine),  # type: ignore[arg-type]
        ],
    )

    for view in ADMIN_VIEWS:
        admin.add_view(view)

    app = Starlette()
    admin.mount_to(app)

    @asgi(path="/admin", is_mount=True, copy_scope=True)
    async def admin_mount(scope: Scope, receive: Receive, send: Send) -> None:
        path = scope.get("path") or "/"
        if not path.startswith("/admin"):
            path = f"/admin{path}"
        if path.endswith("/") and path != "/admin/":
            path = path.rstrip("/")
        scope["path"] = path
        await app(scope, receive, send)

    return admin_mount
