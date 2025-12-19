import strawberry
from graphql.error import GraphQLError
from sqlalchemy import select
from strawberry.types import Info

from backend.apps.users.models import UserModel

from .types import UserType


@strawberry.type
class UserQuery:
    @strawberry.field
    async def user(self, info: Info, id: strawberry.ID) -> UserType:
        user_id = int(id)

        db_session = info.context["db_session"]
        user = await db_session.scalar(select(UserModel).where(UserModel.id == user_id))
        if user is None:
            raise GraphQLError(f"User with id {user_id} not found")
        return UserType.from_model(user)
