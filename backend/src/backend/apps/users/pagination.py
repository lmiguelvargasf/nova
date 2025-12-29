from litestar.pagination import AbstractAsyncCursorPaginator
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.pagination import decode_cursor, encode_cursor

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

    def _statement(self, *, last_id: int, limit: int) -> Select[tuple[UserModel]]:
        stmt = select(UserModel).where(
            UserModel.deleted_at.is_(None),
            UserModel.id > last_id,
        )

        if self._search_string:
            value = f"%{self._search_string}%"
            if self._search_ignore_case:
                stmt = stmt.where(UserModel.email.ilike(value))
            else:
                stmt = stmt.where(UserModel.email.like(value))

        return stmt.order_by(UserModel.id.asc()).limit(limit)

    async def get_items(
        self,
        cursor: str | None,
        results_per_page: int,
    ) -> tuple[list[UserResponse], str | None]:
        last_id = 0
        if cursor is not None:
            decoded = decode_cursor(cursor)
            last_id_raw = decoded.get("last_id")
            if not isinstance(last_id_raw, int) or last_id_raw < 0:
                from litestar.exceptions import HTTPException

                raise HTTPException(status_code=400, detail="Invalid cursor.")
            last_id = last_id_raw

        stmt = self._statement(last_id=last_id, limit=results_per_page + 1)
        result = await self._db_session.execute(stmt)
        users = list(result.scalars())

        has_next = len(users) > results_per_page
        if has_next:
            users = users[:results_per_page]

        next_cursor = None
        if has_next and users:
            next_cursor = encode_cursor({"last_id": users[-1].id})

        service = UserService(self._db_session)
        return [
            service.to_schema(u, schema_type=UserResponse) for u in users
        ], next_cursor
