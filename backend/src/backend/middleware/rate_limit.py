from __future__ import annotations

from litestar import Request
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import DefineMiddleware
from litestar.middleware.rate_limit import RateLimitConfig, get_remote_address
from litestar.security.jwt import Token

from backend.config.base import settings

_EXCLUDED_PATHS = {"/health", "/schema", "/admin"}


def _get_cached_subject(request: Request) -> str | None:
    cached = getattr(request.state, "rate_limit_subject", None)
    if cached is not None:
        return cached or None

    subject: str | None = None
    auth_header = request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            try:
                token = Token.decode(
                    encoded_token=parts[1],
                    secret=settings.jwt_secret,
                    algorithm="HS256",
                )
                subject = token.sub
            except NotAuthorizedException, ValueError:
                subject = None

    request.state.rate_limit_subject = subject or ""
    return subject


def _is_admin_user(request: Request) -> bool:
    if "session" not in request.scope:
        return False
    return "admin_user_id" in request.session


def _is_path_excluded(request: Request) -> bool:
    if _is_admin_user(request):
        return True
    path = request.url.path
    return any(path.startswith(excluded_path) for excluded_path in _EXCLUDED_PATHS)


def _is_authenticated(request: Request) -> bool:
    if _is_path_excluded(request):
        return False
    return _get_cached_subject(request) is not None


def _is_anonymous(request: Request) -> bool:
    if _is_path_excluded(request):
        return False
    return _get_cached_subject(request) is None


def _identifier_for_authenticated(request: Request) -> str:
    subject = _get_cached_subject(request)
    if subject:
        return f"user:{subject}"
    return get_remote_address(request)


def get_rate_limit_middlewares() -> list[DefineMiddleware]:
    anonymous_config = RateLimitConfig(
        rate_limit=("minute", settings.rate_limit_per_minute_anonymous),
        check_throttle_handler=_is_anonymous,
        identifier_for_request=get_remote_address,
    )
    authenticated_config = RateLimitConfig(
        rate_limit=("minute", settings.rate_limit_per_minute_authenticated),
        check_throttle_handler=_is_authenticated,
        identifier_for_request=_identifier_for_authenticated,
    )
    return [anonymous_config.middleware, authenticated_config.middleware]
