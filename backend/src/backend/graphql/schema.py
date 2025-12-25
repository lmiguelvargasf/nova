import strawberry
from strawberry.extensions import QueryDepthLimiter

from backend.apps.users.graphql import UserMutation, UserQuery
from backend.config.base import settings


@strawberry.type
class Query(UserQuery):
    pass


@strawberry.type
class Mutation(UserMutation):
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[QueryDepthLimiter(max_depth=settings.graphql_max_depth)],
)
