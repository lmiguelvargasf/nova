from graphql.error import GraphQLError


class UserNotAuthenticatedError(GraphQLError):
    def __init__(self) -> None:
        super().__init__("User is not authenticated")
