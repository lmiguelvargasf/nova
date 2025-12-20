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
    session_secret: str | None = None,
) -> Starlette:
    """Create the Starlette Admin application."""
    secret = (session_secret or settings.admin_session_secret or "").strip()
    if not secret:
        raise RuntimeError(
            "ADMIN_SESSION_SECRET must be set to enable the Starlette-Admin UI."
        )

    db_engine = engine or alchemy_config.get_engine()
    admin = BaseAdmin(
        title="Admin",
        base_url="/admin",
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
    app.router.redirect_slashes = False
    admin.mount_to(app, redirect_slashes=False)
    return app


def create_admin_handler(
    *,
    engine: AsyncEngine | None = None,
    session_secret: str | None = None,
    admin_asgi_app: ASGIApp | None = None,
) -> ASGIRouteHandler:
    """Create a Litestar ASGI handler that mounts the Starlette Admin app."""
    app = admin_asgi_app or create_admin_app(
        engine=engine, session_secret=session_secret
    )

    @asgi(path="/admin", is_mount=True, copy_scope=True)
    async def admin_mount(scope: Scope, receive: Receive, send: Send) -> None:
        prefix = "/admin"
        path = scope.get("path", "")
        # Litestar mounts always include a trailing slash; normalize for Admin routes.
        if path in ("", "/"):
            normalized_path = f"{prefix}/"
        else:
            trimmed = path.rstrip("/")
            if trimmed == prefix:
                normalized_path = f"{prefix}/"
            elif trimmed.startswith(prefix):
                normalized_path = trimmed
            else:
                normalized_path = prefix + trimmed
        if normalized_path != path:
            scope["path"] = normalized_path
            raw_path = scope.get("raw_path")
            if isinstance(raw_path, (bytes, bytearray)):
                scope["raw_path"] = normalized_path.encode()
        await app(scope, receive, send)

    return admin_mount
