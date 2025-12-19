from typing import ClassVar

from sqladmin import Admin, ModelView
from starlette.applications import Starlette

from backend.admin_auth import AdminAuth
from backend.apps.users.models import UserModel
from backend.config.alchemy import alchemy_config
from backend.config.base import settings

starlette_app = Starlette()


class UserAdmin(ModelView, model=UserModel):
    column_list: ClassVar[list] = [
        UserModel.id,
        UserModel.email,
        UserModel.first_name,
        UserModel.last_name,
        UserModel.is_admin,
        UserModel.is_active,
    ]

    async def on_model_change(
        self, data: dict, model: UserModel, is_created: bool, request
    ) -> None:  # type: ignore[override]
        # SQLAdmin generates a form field for `password_hash`. We interpret it as a
        # plain-text password and hash it before persisting.
        raw_password = data.get("password_hash")

        if raw_password:
            from backend.security.passwords import hash_password

            data["password_hash"] = hash_password(str(raw_password))
        else:
            # On update, an empty password field should not overwrite the existing hash.
            if not is_created:
                data.pop("password_hash", None)


admin = Admin(
    starlette_app,
    engine=alchemy_config.get_engine(),
    # We mount the Starlette app under Litestar, so keep SQLAdmin rooted at "/".
    base_url="/",
    title="Nova Admin",
    authentication_backend=AdminAuth(secret_key=settings.admin_session_secret or ""),
)
admin.add_view(UserAdmin)
