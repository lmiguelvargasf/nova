from starlette.requests import Request
from starlette_admin import action
from starlette_admin.contrib.sqla import ModelView

from backend.apps.users.models import UserModel
from backend.apps.users.tasks import deactivate_inactive_users


class UserAdminView(ModelView):
    label = "Users"
    name = "User"
    identity = "user"

    exclude_fields_from_list = ("password_hash",)
    exclude_fields_from_detail = ("password_hash",)
    exclude_fields_from_create = (
        "password_hash",
        "created_at",
        "updated_at",
        "deleted_at",
        "last_login_at",
    )
    exclude_fields_from_edit = (
        "password_hash",
        "created_at",
        "updated_at",
        "deleted_at",
        "last_login_at",
    )

    searchable_fields = ("email", "first_name", "last_name")
    sortable_fields = (
        "id",
        "email",
        "first_name",
        "last_name",
        "is_admin",
        "is_active",
        "created_at",
        "updated_at",
    )

    @action(
        name="run_inactivity_sweep",
        text="Run Inactivity Sweep",
        confirmation=(
            "This will trigger a background task to deactivate selected users "
            "that haven't logged in for the configured cutoff days."
        ),
        submit_btn_text="Run Sweep",
        submit_btn_class="btn-danger",
    )
    async def run_inactivity_sweep(self, request: Request, pks: list[object]) -> str:
        # pks is a list of selected primary keys (ids)
        user_ids = [int(str(pk)) for pk in pks] if pks else None

        deactivate_inactive_users.delay(user_ids=user_ids)

        if user_ids:
            return f"Inactivity sweep queued for {len(user_ids)} selected users."
        return "Inactivity sweep task has been queued for all users."


view = UserAdminView(UserModel, icon="fa fa-user")
