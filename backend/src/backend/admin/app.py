from litestar import asgi
from litestar.handlers.asgi_handlers import ASGIRouteHandler
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette_admin import BaseAdmin
from starlette_admin.contrib.sqla.middleware import DBSessionMiddleware

from backend.apps.users.models import UserModel
from backend.config.alchemy import alchemy_config
from backend.config.base import settings

from .auth import BackendAdminAuthProvider
from .views import UserAdminView


def create_admin_app(
    *,
    engine: AsyncEngine | None = None,
) -> Starlette:
    """Create the Starlette Admin application."""
    secret = settings.admin_session_secret
    db_engine = engine or alchemy_config.get_engine()
    admin = BaseAdmin(
        title="Admin",
        auth_provider=BackendAdminAuthProvider(engine=db_engine),
        middlewares=[
            Middleware(
                SessionMiddleware,
                secret_key=secret,
                same_site="lax",
            ),
            Middleware(DBSessionMiddleware, engine=db_engine),
        ],
    )
    admin.add_view(UserAdminView(UserModel))

    app = Starlette()
    admin.mount_to(app)
    return app


def create_admin_handler(
    *,
    engine: AsyncEngine | None = None,
    admin_asgi_app: ASGIApp | None = None,
) -> ASGIRouteHandler:
    """Create a Litestar ASGI handler that mounts the Starlette Admin app."""
    app = admin_asgi_app or create_admin_app(engine=engine)

    @asgi(path="/admin", is_mount=True, copy_scope=True)
    async def admin_mount(scope: Scope, receive: Receive, send: Send) -> None:
        # Litestar strips /admin prefix; restore it for Starlette Admin
        path = scope.get("path") or "/"
        if not path.startswith("/admin"):
            path = f"/admin{path}"
        # Normalize trailing slash (Starlette routes don't have trailing slashes)
        if path.endswith("/") and path != "/admin/":
            path = path[:-1]
        scope["path"] = path
        await app(scope, receive, send)

    return admin_mount
