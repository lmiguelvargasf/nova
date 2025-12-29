from collections.abc import Iterable

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from backend.apps.users.models import UserModel
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
    async def user_by_id(
        self,
        info: Info[GraphQLContext, None],
        id: strawberry.relay.GlobalID,
    ) -> UserType:
        try:
            return await id.resolve_node(info, ensure_type=UserType)
        except TypeError as e:
            raise UserNotFoundError(str(id)) from e

    @strawberry.relay.connection(
        strawberry.relay.ListConnection[UserType],
        permission_classes=[IsAuthenticated],
    )
    async def users(self, info: Info[GraphQLContext, None]) -> Iterable[UserType]:
        stmt = (
            select(UserModel)
            .where(UserModel.deleted_at.is_(None))
            .order_by(UserModel.created_at.asc(), UserModel.id.asc())
        )
        result = await info.context.db_session.execute(stmt)
        users = list(result.scalars())
        return [UserType.from_model(u) for u in users]
