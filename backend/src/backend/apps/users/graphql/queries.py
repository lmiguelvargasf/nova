import strawberry
from advanced_alchemy.exceptions import NotFoundError
from graphql.error import GraphQLError
from strawberry.types import Info

from backend.apps.users.services import UserService

from .types import UserType


class UserNotFoundError(GraphQLError):
    def __init__(self, user_id: int) -> None:
        super().__init__(
            f"User with id {user_id} not found",
            extensions={"code": "NOT_FOUND"},
        )


@strawberry.type
class UserQuery:
    @strawberry.field
    async def user(self, info: Info, id: strawberry.ID) -> UserType:
        user_id = int(id)
        user_service: UserService = info.context["user_service"]
        try:
            user = await user_service.get(user_id)
        except NotFoundError:
            raise UserNotFoundError(user_id) from None
        return UserType.from_model(user)
