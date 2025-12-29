from dataclasses import dataclass
from typing import Self

import strawberry
from strawberry import relay

from backend.apps.users.models import UserModel


@strawberry.type
@dataclass
class UserType(relay.Node):
    id: relay.NodeID[int]
    first_name: str
    last_name: str
    email: str

    @classmethod
    def from_model(cls, user: UserModel) -> Self:
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )


@strawberry.type
@dataclass
class LoginResponse:
    token: str
    user: UserType
    reactivated: bool
