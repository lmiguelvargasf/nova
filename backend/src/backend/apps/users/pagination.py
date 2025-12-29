import datetime

from litestar.exceptions import HTTPException
from litestar.pagination import AbstractAsyncCursorPaginator
from sqlalchemy import Select, and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.pagination import (
    compute_pagination_context_hash,
    decode_cursor,
    encode_cursor,
)
from backend.config.base import settings

from .models import UserModel
from .schemas import UserResponse
from .services import UserService


class UserCursorPaginator(AbstractAsyncCursorPaginator[str, UserResponse]):
    def __init__(
        self,
        *,
        db_session: AsyncSession,
        search_string: str | None,
        search_ignore_case: bool,
    ) -> None:
        self._db_session = db_session
        self._search_string = search_string
        self._search_ignore_case = search_ignore_case

    def _context_hash(self) -> str:
        return compute_pagination_context_hash(
            sort="created_at_asc_id_asc",
            filters={
                "search_string": self._search_string or "",
                "search_ignore_case": self._search_ignore_case,
            },
        )

    def _statement(
        self,
        *,
        last_created_at: datetime.datetime,
        last_id: int,
        limit: int,
    ) -> Select[tuple[UserModel]]:
        stmt = select(UserModel).where(
            UserModel.deleted_at.is_(None),
            or_(
                UserModel.created_at > last_created_at,
                and_(
                    UserModel.created_at == last_created_at,
                    UserModel.id > last_id,
                ),
            ),
        )

        if self._search_string:
            value = f"%{self._search_string}%"
            if self._search_ignore_case:
                stmt = stmt.where(UserModel.email.ilike(value))
            else:
                stmt = stmt.where(UserModel.email.like(value))

        return stmt.order_by(UserModel.created_at.asc(), UserModel.id.asc()).limit(
            limit
        )

    async def get_items(
        self,
        cursor: str | None,
        results_per_page: int,
    ) -> tuple[list[UserResponse], str | None]:
        context_hash = self._context_hash()

        last_id = 0
        last_created_at = datetime.datetime.min.replace(tzinfo=datetime.UTC)
        if cursor is not None:
            decoded = decode_cursor(
                cursor=cursor,
                secret=settings.jwt_secret,
                expected_context_hash=context_hash,
            )
            last_id_raw = decoded.get("last_id")
            last_created_at_raw = decoded.get("last_created_at")
            if (
                not isinstance(last_id_raw, int)
                or last_id_raw < 0
                or not isinstance(last_created_at_raw, str)
            ):
                raise HTTPException(status_code=400, detail="Invalid cursor.")
            try:
                last_created_at = datetime.datetime.fromisoformat(last_created_at_raw)
            except ValueError as e:
                raise HTTPException(status_code=400, detail="Invalid cursor.") from e
            last_id = last_id_raw

        stmt = self._statement(
            last_created_at=last_created_at,
            last_id=last_id,
            limit=results_per_page + 1,
        )
        result = await self._db_session.execute(stmt)
        users = list(result.scalars())

        has_next = len(users) > results_per_page
        if has_next:
            users = users[:results_per_page]

        next_cursor = None
        if has_next and users:
            next_cursor = encode_cursor(
                payload={
                    "v": 1,
                    "context_hash": context_hash,
                    "last_id": users[-1].id,
                    "last_created_at": users[-1].created_at.isoformat(),
                },
                secret=settings.jwt_secret,
            )

        service = UserService(self._db_session)
        return [
            service.to_schema(u, schema_type=UserResponse) for u in users
        ], next_cursor
