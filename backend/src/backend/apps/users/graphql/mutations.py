import datetime

import strawberry
from advanced_alchemy.exceptions import DuplicateKeyError, RepositoryError
from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHash,
    VerificationError,
    VerifyMismatchError,
)
from graphql.error import GraphQLError
from strawberry.types import Info

from backend.apps.users.services import UserService
from backend.auth.jwt import jwt_auth

from .inputs import UserInput
from .types import LoginResponse, UserType


class UserAlreadyExistsError(GraphQLError):
    def __init__(self, email: str) -> None:
        super().__init__(f"User with email '{email}' already exists.")


class InvalidCredentialsError(GraphQLError):
    def __init__(self) -> None:
        super().__init__(
            "Invalid credentials",
            extensions={"code": "INVALID_CREDENTIALS"},
        )


class JWTTokenCreationError(RuntimeError):
    def __init__(self) -> None:
        super().__init__("JWTAuth does not expose a supported token creation method.")


def _create_access_token(*, user_id: int, email: str, is_admin: bool) -> str:
    token_extras = {"email": email, "is_admin": is_admin}
    if hasattr(jwt_auth, "create_token"):
        return str(
            jwt_auth.create_token(identifier=str(user_id), token_extras=token_extras)
        )
    if hasattr(jwt_auth, "encode"):
        return str(jwt_auth.encode(identifier=str(user_id), token_extras=token_extras))
    raise JWTTokenCreationError


@strawberry.type
class UserMutation:
    @strawberry.mutation
    async def create_user(self, info: Info, user_input: UserInput) -> UserType:
        db_session = info.context["db_session"]
        user_service: UserService = info.context["user_service"]
        existing_user = await user_service.get_one_or_none(email=user_input.email)
        if existing_user:
            raise UserAlreadyExistsError(user_input.email)

        try:
            ph = PasswordHasher()
            user = await user_service.create(
                {
                    "email": user_input.email,
                    "password_hash": ph.hash(user_input.password),
                    "first_name": user_input.first_name,
                    "last_name": user_input.last_name,
                    "is_admin": False,
                    "is_active": True,
                },
                auto_commit=True,
            )
        except DuplicateKeyError:
            await db_session.rollback()
            raise UserAlreadyExistsError(user_input.email) from None
        except RepositoryError as exc:
            await db_session.rollback()
            detail = exc.detail or "Unable to create user."
            raise GraphQLError(detail) from None

        return UserType.from_model(user)

    @strawberry.mutation
    async def login(self, info: Info, email: str, password: str) -> LoginResponse:
        email_clean = (email or "").strip().lower()
        if not email_clean or not password:
            raise InvalidCredentialsError

        db_session = info.context["db_session"]
        user_service: UserService = info.context["user_service"]
        user = await user_service.get_one_or_none(email=email_clean)

        if user is None or not user.is_active:
            raise InvalidCredentialsError

        ph = PasswordHasher()
        try:
            ok = ph.verify(user.password_hash, password)
        except (VerifyMismatchError, InvalidHash, VerificationError):
            ok = False
        except Exception:  # noqa: BLE001 # security boundary: do not leak verification errors
            ok = False

        if not ok:
            raise InvalidCredentialsError

        user.last_login_at = datetime.datetime.now(datetime.UTC)
        await db_session.commit()

        token = _create_access_token(
            user_id=user.id,
            email=user.email,
            is_admin=user.is_admin,
        )
        return LoginResponse(token=token, user=UserType.from_model(user))
