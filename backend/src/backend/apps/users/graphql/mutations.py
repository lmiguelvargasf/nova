import strawberry
from advanced_alchemy.exceptions import DuplicateKeyError, RepositoryError
from argon2 import PasswordHasher
from graphql.error import GraphQLError
from strawberry.types import Info

from backend.graphql.context import GraphQLContext

from .inputs import UserInput
from .types import UserType


class UserAlreadyExistsError(GraphQLError):
    def __init__(self, email: str) -> None:
        super().__init__(f"User with email '{email}' already exists.")


@strawberry.type
class UserMutation:
    @strawberry.mutation
    async def create_user(
        self, info: Info[GraphQLContext, None], user_input: UserInput
    ) -> UserType:
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

        return UserType.from_model(user)
