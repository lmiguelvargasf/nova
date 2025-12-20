from litestar import asgi
from litestar.handlers.asgi_handlers import ASGIRouteHandler
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.types import Receive, Scope, Send
from starlette_admin import BaseAdmin
from starlette_admin.contrib.sqla.middleware import DBSessionMiddleware

from backend.config.alchemy import alchemy_config
from backend.config.base import settings

from .auth import BackendAdminAuthProvider
from .views import ADMIN_VIEWS


def create_admin_handler(
    *,
    engine: AsyncEngine | None = None,
) -> ASGIRouteHandler:
    """Create a Litestar ASGI handler that mounts the Starlette Admin app."""
    db_engine = engine or alchemy_config.get_engine()

    admin = BaseAdmin(
        title="Admin",
        auth_provider=BackendAdminAuthProvider(engine=db_engine),
        middlewares=[
            Middleware(
                SessionMiddleware,
                secret_key=settings.admin_session_secret,
                same_site="lax",
            ),
            Middleware(DBSessionMiddleware, engine=db_engine),
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
