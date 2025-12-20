import strawberry
from advanced_alchemy.exceptions import DuplicateKeyError, RepositoryError
from argon2 import PasswordHasher
from graphql.error import GraphQLError
from strawberry.types import Info

from backend.apps.users.services import UserService

from .inputs import UserInput
from .types import UserType


@strawberry.type
class UserMutation:
    @strawberry.mutation
    async def create_user(self, info: Info, user_input: UserInput) -> UserType:
        db_session = info.context["db_session"]
        user_service: UserService = info.context["user_service"]
        existing_user = await user_service.get_one_or_none(email=user_input.email)
        if existing_user:
            raise GraphQLError(f"User with email '{user_input.email}' already exists.")

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
            raise GraphQLError(
                f"User with email '{user_input.email}' already exists."
            ) from None
        except RepositoryError as exc:
            await db_session.rollback()
            detail = exc.detail or "Unable to create user."
            raise GraphQLError(detail) from None

        return UserType.from_model(user)
