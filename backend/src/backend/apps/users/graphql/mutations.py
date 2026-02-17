import strawberry
from advanced_alchemy.exceptions import RepositoryError
from graphql.error import GraphQLError
from strawberry.types import Info

from backend.apps.users.auth import create_access_token
from backend.apps.users.services import (
    InvalidCredentialsError as InvalidCredentialsServiceError,
)
from backend.apps.users.services import (
    UserAlreadyExistsError as UserAlreadyExistsServiceError,
)
from backend.apps.users.services import UserFieldEmptyError
from backend.graphql.context import GraphQLContext
from backend.graphql.permissions import IsAuthenticated

from .errors import UserNotAuthenticatedError
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


def _raise_empty_field_error(field_name: str) -> None:
    if field_name == "email":
        raise EmptyEmailError from None
    if field_name == "first_name":
        raise EmptyFirstNameError from None
    if field_name == "last_name":
        raise EmptyLastNameError from None
    if field_name == "password":
        raise EmptyPasswordError from None
    raise EmptyUserFieldError(field_name) from None


@strawberry.type
class UserMutation:
    @strawberry.mutation
    async def create_user(
        self, info: Info[GraphQLContext, None], user_input: UserInput
    ) -> LoginResponse:
        db_session = info.context.db_session
        user_service = info.context.services.users

        try:
            user = await user_service.create_user_account(
                db_session=db_session,
                email=user_input.email,
                password=user_input.password,
                first_name=user_input.first_name,
                last_name=user_input.last_name,
                is_admin=False,
                is_active=True,
            )
        except UserAlreadyExistsServiceError as exc:
            raise UserAlreadyExistsError(exc.email) from None
        except RepositoryError as exc:
            await db_session.rollback()
            detail = exc.detail or "Unable to create user."
            raise GraphQLError(detail) from None

        token = create_access_token(user)
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
        try:
            updated_user = await user_service.apply_user_updates(
                db_session=db_session,
                user=user,
                email=user_input.email,
                first_name=user_input.first_name,
                last_name=user_input.last_name,
                password=user_input.password,
            )
        except UserAlreadyExistsServiceError as exc:
            raise UserAlreadyExistsError(exc.email) from None
        except UserFieldEmptyError as exc:
            _raise_empty_field_error(exc.field_name)

        return UserType.from_model(updated_user)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def soft_delete_current_user(self, info: Info[GraphQLContext, None]) -> bool:
        db_session = info.context.db_session
        user_service = info.context.services.users
        user = info.context.user
        if user is None:
            raise UserNotAuthenticatedError

        await user_service.soft_delete_user(db_session=db_session, user=user)
        return True

    @strawberry.mutation
    async def login(
        self, info: Info[GraphQLContext, None], email: str, password: str
    ) -> LoginResponse:
        db_session = info.context.db_session
        user_service = info.context.services.users
        try:
            user, reactivated = await user_service.authenticate_for_login(
                db_session=db_session,
                email=email,
                password=password,
            )
        except InvalidCredentialsServiceError:
            raise InvalidCredentialsError from None

        token = create_access_token(user)
        return LoginResponse(
            token=token,
            user=UserType.from_model(user),
            reactivated=reactivated,
        )
