import strawberry
from advanced_alchemy.exceptions import NotFoundError
from graphql.error import GraphQLError
from strawberry.types import Info

from backend.graphql.context import GraphQLContext
from backend.graphql.permissions import IsAuthenticated

from .errors import UserNotAuthenticatedError
from .types import UserType


class UserNotFoundError(GraphQLError):
    def __init__(self, user_id: int) -> None:
        super().__init__(
            f"User with id {user_id} not found",
            extensions={"code": "NOT_FOUND"},
        )


@strawberry.type
class UserQuery:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def me(self, info: Info[GraphQLContext, None]) -> UserType:
        user = info.context.user
        if user is None:
            raise UserNotAuthenticatedError
        return UserType.from_model(user)

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def user(
        self, info: Info[GraphQLContext, None], id: strawberry.ID
    ) -> UserType:
        user_id = int(id)
        try:
            user = await info.context.services.users.get(user_id)
        except NotFoundError:
            raise UserNotFoundError(user_id) from None
        return UserType.from_model(user)
