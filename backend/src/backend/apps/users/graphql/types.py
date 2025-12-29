from collections.abc import Iterable
from dataclasses import dataclass
from typing import Self

import strawberry

from backend.apps.users.models import UserModel

from .errors import UserNotFoundError


@strawberry.type
@dataclass
class UserType(strawberry.relay.Node):
    id: strawberry.relay.NodeID[int]
    first_name: str
    last_name: str
    email: str

    @classmethod
    async def resolve_nodes(
        cls,
        *,
        info: strawberry.Info,
        node_ids: Iterable[str],
        required: bool = False,
    ) -> Iterable[Self | None]:  # type: ignore
        services = info.context.services
        node_ids_list = list(node_ids)
        ids = []
        for nid in node_ids_list:
            try:
                ids.append(int(nid))
            except ValueError:
                if required:
                    raise UserNotFoundError from None
                ids.append(None)

        valid_ids = [i for i in ids if i is not None]
        if not valid_ids:
            return [None] * len(node_ids_list)

        users = await services.users.list(id__in=valid_ids)
        user_map = {u.id: cls.from_model(u) for u in users}

        resolved = []
        for nid in node_ids_list:
            try:
                uid = int(nid)
                if uid in user_map:
                    resolved.append(user_map[uid])
                elif required:
                    raise UserNotFoundError
                else:
                    resolved.append(None)
            except ValueError:
                resolved.append(None)

        return resolved

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
