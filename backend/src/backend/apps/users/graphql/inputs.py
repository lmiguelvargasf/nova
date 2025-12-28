from dataclasses import dataclass

import strawberry


@strawberry.input
@dataclass
class UserInput:
    email: str
    password: str
    first_name: str
    last_name: str


@strawberry.input
@dataclass
class UpdateUserInput:
    email: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
