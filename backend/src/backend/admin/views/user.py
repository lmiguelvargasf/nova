from starlette_admin.contrib.sqla import ModelView

from backend.apps.users.models import UserModel


class UserAdminView(ModelView):
    icon = "fa fa-user"

    exclude_fields_from_list = ("password_hash",)
    exclude_fields_from_detail = ("password_hash",)
    exclude_fields_from_create = ("password_hash",)
    exclude_fields_from_edit = ("password_hash",)

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


VIEW = (UserAdminView, UserModel)
