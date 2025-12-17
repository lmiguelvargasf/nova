from dataclasses import dataclass
from typing import Self

import strawberry
from piccolo.apps.user.tables import BaseUser


@strawberry.type
@dataclass
class UserType:
    id: strawberry.ID
    username: str
    first_name: str
    last_name: str
    email: str

    @classmethod
    def from_model(cls, user: BaseUser) -> Self:
        return cls(
            id=strawberry.ID(str(user.id)),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )
