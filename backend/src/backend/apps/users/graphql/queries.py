import strawberry
from advanced_alchemy.exceptions import NotFoundError
from graphql.error import GraphQLError
from strawberry.types import Info

from ..services import UserService
from .types import UserType


@strawberry.type
class UserQuery:
    @strawberry.field
    async def user(self, info: Info, id: strawberry.ID) -> UserType:
        user_id = int(id)
        user_service: UserService = info.context["user_service"]
        try:
            user = await user_service.get(user_id)
        except NotFoundError:
            raise GraphQLError(f"User with id {user_id} not found") from None
        return UserType.from_model(user)
