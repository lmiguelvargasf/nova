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

from backend.auth.jwt import jwt_auth
from backend.graphql.context import GraphQLContext
from backend.graphql.permissions import IsAuthenticated

from .inputs import UpdateUserInput, UserInput
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


class EmptyUserFieldError(GraphQLError):
    def __init__(self, field_name: str) -> None:
        super().__init__(f"{field_name} cannot be empty.")


class EmptyEmailError(GraphQLError):
    def __init__(self) -> None:
        super().__init__("Email cannot be empty.")


class EmptyFirstNameError(GraphQLError):
    def __init__(self) -> None:
        super().__init__("First name cannot be empty.")


class EmptyLastNameError(GraphQLError):
    def __init__(self) -> None:
        super().__init__("Last name cannot be empty.")


class EmptyPasswordError(GraphQLError):
    def __init__(self) -> None:
        super().__init__("Password cannot be empty.")


class UserNotAuthenticatedError(GraphQLError):
    def __init__(self) -> None:
        super().__init__("User is not authenticated")


def _create_access_token(*, user_id: int, email: str, is_admin: bool) -> str:
    """Create a JWT token for the given user."""
    return str(
        jwt_auth.create_token(
            identifier=str(user_id),
            token_extras={"email": email, "is_admin": is_admin},
        )
    )


@strawberry.type
class UserMutation:
    @strawberry.mutation
    async def create_user(
        self, info: Info[GraphQLContext, None], user_input: UserInput
    ) -> LoginResponse:
        db_session = info.context.db_session
        user_service = info.context.services.users
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

        token = _create_access_token(
            user_id=user.id,
            email=user.email,
            is_admin=user.is_admin,
        )
        return LoginResponse(
            token=token,
            user=UserType.from_model(user),
            reactivated=False,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def update_current_user(
        self, info: Info[GraphQLContext, None], user_input: UpdateUserInput
    ) -> UserType:
        db_session = info.context.db_session
        user_service = info.context.services.users
        user = info.context.user
        if user is None:
            raise UserNotAuthenticatedError

        has_updates = False

        if user_input.email is not None:
            email = user_input.email.strip()
            if not email:
                raise EmptyEmailError
            if email != user.email:
                existing_user = await user_service.get_one_or_none(email=email)
                if existing_user and existing_user.id != user.id:
                    raise UserAlreadyExistsError(email)
            user.email = email
            has_updates = True

        if user_input.first_name is not None:
            first_name = user_input.first_name.strip()
            if not first_name:
                raise EmptyFirstNameError
            user.first_name = first_name
            has_updates = True

        if user_input.last_name is not None:
            last_name = user_input.last_name.strip()
            if not last_name:
                raise EmptyLastNameError
            user.last_name = last_name
            has_updates = True

        if user_input.password is not None:
            if not user_input.password:
                raise EmptyPasswordError
            ph = PasswordHasher()
            user.password_hash = ph.hash(user_input.password)
            has_updates = True

        if has_updates:
            await db_session.commit()

        return UserType.from_model(user)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def soft_delete_current_user(self, info: Info[GraphQLContext, None]) -> bool:
        db_session = info.context.db_session
        user = info.context.user
        if user is None:
            raise UserNotAuthenticatedError

        user.soft_delete()
        await db_session.commit()
        return True

    @strawberry.mutation
    async def login(
        self, info: Info[GraphQLContext, None], email: str, password: str
    ) -> LoginResponse:
        email_clean = (email or "").strip().lower()
        if not email_clean or not password:
            raise InvalidCredentialsError

        db_session = info.context.db_session
        user_service = info.context.services.users
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

        reactivated = False
        if user.deleted_at is not None:
            user.deleted_at = None
            reactivated = True

        user.last_login_at = datetime.datetime.now(datetime.UTC)
        await db_session.commit()

        token = _create_access_token(
            user_id=user.id,
            email=user.email,
            is_admin=user.is_admin,
        )
        return LoginResponse(
            token=token,
            user=UserType.from_model(user),
            reactivated=reactivated,
        )
