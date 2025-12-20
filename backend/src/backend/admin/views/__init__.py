from starlette_admin.contrib.sqla import ModelView

from .user import VIEW as USER_VIEW

ADMIN_VIEWS: list[tuple[type[ModelView], type]] = [
    USER_VIEW,
]
