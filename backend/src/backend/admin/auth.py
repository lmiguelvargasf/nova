from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerificationError, VerifyMismatchError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider, LoginFailed

from backend.apps.users.models import UserModel


class BackendAdminAuthProvider(AuthProvider):
    def __init__(self, *, engine: AsyncEngine) -> None:
        super().__init__()
        self._engine = engine

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        email = (username or "").strip().lower()
        if not email or not password:
            raise LoginFailed("Invalid username or password")

        ph = PasswordHasher()
        async with AsyncSession(self._engine, expire_on_commit=False) as session:
            user = await session.scalar(
                select(UserModel).where(UserModel.email == email)
            )

        if user is None or not user.is_admin or not user.is_active:
            raise LoginFailed("Invalid username or password")

        try:
            ok = ph.verify(user.password_hash, password)
        except (VerifyMismatchError, InvalidHash, VerificationError):
            ok = False
        except Exception:  # security boundary: do not leak verification errors
            ok = False

        if not ok:
            raise LoginFailed("Invalid username or password")

        request.session.clear()
        request.session.update({"admin_user_id": user.id})
        return response

    async def is_authenticated(self, request: Request) -> bool:
        user_id = request.session.get("admin_user_id")
        if user_id is None:
            return False

        try:
            user_id_int = int(user_id)
        except (TypeError, ValueError):
            request.session.clear()
            return False

        async with AsyncSession(self._engine, expire_on_commit=False) as session:
            user = await session.get(UserModel, user_id_int)

        if user is None or not user.is_admin or not user.is_active:
            request.session.clear()
            return False

        request.state.user = user
        return True

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response

    def get_admin_user(self, request: Request) -> AdminUser | None:
        user = getattr(request.state, "user", None)
        if user is None:
            return None
        return AdminUser(username=str(getattr(user, "email", "Administrator")))
