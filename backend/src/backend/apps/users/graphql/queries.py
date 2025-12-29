from collections.abc import Iterable

import strawberry
from advanced_alchemy.exceptions import NotFoundError
from strawberry.types import Info

from backend.graphql.context import GraphQLContext
from backend.graphql.permissions import IsAuthenticated

from .errors import UserNotAuthenticatedError, UserNotFoundError
from .types import UserType


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
        try:
            user_id = int(id)
        except ValueError:
            # Try to decode global ID if it's not an int?
            # For now assume it's an int as per previous implementation
            # or maybe we should support Global ID here too?
            # Let's keep it simple and assume int ID for this legacy field.
            # But if it fails, maybe it is a global ID?
            # Let's just catch ValueError and raise UserNotFoundError or Invalid ID
            raise UserNotFoundError(id) from None

        try:
            user = await info.context.services.users.get(user_id)
        except NotFoundError:
            raise UserNotFoundError(user_id) from None
        return UserType.from_model(user)

    @strawberry.relay.connection(strawberry.relay.ListConnection[UserType])
    async def users(self, info: Info[GraphQLContext, None]) -> Iterable[UserType]:
        users = await info.context.services.users.list()
        return [UserType.from_model(u) for u in users]
