from functools import cached_property

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.litestar.controller import BaseContext

from backend.apps.users.models import UserModel
from backend.apps.users.services import UserService


class Services:
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    @cached_property
    def users(self) -> UserService:
        return UserService(self._db_session)


class GraphQLContext(BaseContext, kw_only=True):
    db_session: AsyncSession
    services: Services
    user: UserModel | None = None
