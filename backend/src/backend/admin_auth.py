from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from backend.apps.users.models import UserModel
from backend.config.alchemy import alchemy_config
from backend.security.passwords import verify_password


class AdminAuth(AuthenticationBackend):
    """
    SQLAdmin authentication backed by the main UserModel table.

    We treat SQLAdmin's login form "username" field as the user's email.
    """

    session_key = "admin_user_id"

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = str(form.get("username", "")).strip().lower()
        password = str(form.get("password", ""))

        if not email or not password:
            return False

        async with alchemy_config.get_session() as session:
            user = await session.scalar(
                select(UserModel).where(UserModel.email == email)
            )
            if user is None or not user.is_active or not user.is_admin:
                return False
            if not verify_password(password=password, password_hash=user.password_hash):
                return False

        request.session[self.session_key] = user.id
        return True

    async def logout(self, request: Request) -> Response | bool:
        request.session.clear()
        return RedirectResponse(request.url_for("admin:login"), status_code=302)

    async def authenticate(self, request: Request) -> Response | bool:
        user_id = request.session.get(self.session_key)
        if not user_id:
            return False

        async with alchemy_config.get_session() as session:
            user = await session.get(UserModel, user_id)
            if user is None or not user.is_active or not user.is_admin:
                request.session.clear()
                return False

        return True
