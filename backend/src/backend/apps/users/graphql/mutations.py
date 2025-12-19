import strawberry
from graphql.error import GraphQLError
from sqlalchemy import select
from strawberry.types import Info

from backend.apps.users.models import UserModel
from backend.security.passwords import hash_password

from .inputs import UserInput
from .types import UserType


@strawberry.type
class UserMutation:
    @strawberry.mutation
    async def create_user(self, info: Info, user_input: UserInput) -> UserType:
        db_session = info.context["db_session"]

        existing_user = await db_session.scalar(
            select(UserModel).where(UserModel.email == user_input.email)
        )
        if existing_user:
            raise GraphQLError(f"User with email '{user_input.email}' already exists.")

        user = UserModel(
            email=user_input.email,
            password_hash=hash_password(user_input.password),
            first_name=user_input.first_name,
            last_name=user_input.last_name,
            is_admin=False,
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()

        return UserType.from_model(user)
