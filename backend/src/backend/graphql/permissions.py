from strawberry.permission import BasePermission
from strawberry.types import Info

from backend.graphql.context import GraphQLContext


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    async def has_permission(
        self, source: object, info: Info[GraphQLContext, None], **kwargs: object
    ) -> bool:
        return info.context.user is not None
