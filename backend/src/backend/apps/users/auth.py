from backend.apps.users.models import UserModel
from backend.auth.jwt import jwt_auth


def create_access_token(user: UserModel) -> str:
    """Create a JWT token for the given user."""
    return str(
        jwt_auth.create_token(
            identifier=str(user.id),
            token_extras={"email": user.email, "is_admin": user.is_admin},
        )
    )
