from msgspec import Struct


class UserResponse(Struct):
    id: int
    email: str
    first_name: str
    last_name: str


class UserCreate(Struct):
    email: str
    password: str
    first_name: str
    last_name: str


class UserUpdate(Struct):
    email: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class LoginRequest(Struct):
    email: str
    password: str


class LoginResponse(Struct):
    token: str
    user: UserResponse
    reactivated: bool


class DeleteResponse(Struct):
    deleted: bool
