import strawberry
from graphql.error import GraphQLError
from piccolo.apps.user.tables import BaseUser

from .types import UserType


@strawberry.type
class UserQuery:
    @strawberry.field
    async def user(self, id: strawberry.ID) -> UserType:
        user_id = int(id)
        user = await BaseUser.objects().get(BaseUser.id == user_id)
        if user is None:
            raise GraphQLError(f"User with id {user_id} not found")
        return UserType.from_model(user)
