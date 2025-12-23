from dataclasses import dataclass
from typing import Self

import strawberry

from backend.apps.users.models import UserModel


@strawberry.type
@dataclass
class UserType:
    id: strawberry.ID
    first_name: str
    last_name: str
    email: str

    @classmethod
    def from_model(cls, user: UserModel) -> Self:
        return cls(
            id=strawberry.ID(str(user.id)),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )
