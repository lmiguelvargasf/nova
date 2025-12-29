from graphql.error import GraphQLError


class UserNotAuthenticatedError(GraphQLError):
    def __init__(self) -> None:
        super().__init__("User is not authenticated")


class UserNotFoundError(GraphQLError):
    def __init__(self, user_id: str | int | None = None) -> None:
        message = f"User with id {user_id} not found" if user_id else "User not found"
        super().__init__(message, extensions={"code": "NOT_FOUND"})
