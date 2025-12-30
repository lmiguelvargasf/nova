import asyncio
import datetime

from sqlalchemy import and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.apps.users.models import UserModel
from backend.celery_app import app, get_task_session


@app.task
def deactivate_inactive_users(
    cutoff_days: int = 7,
    user_ids: list[int] | None = None,
) -> int:
    return asyncio.run(_deactivate_inactive_users_async(cutoff_days, user_ids))


async def _deactivate_inactive_users_async(
    cutoff_days: int,
    user_ids: list[int] | None = None,
    *,
    session: AsyncSession | None = None,
) -> int:
    cutoff_date = datetime.datetime.now(datetime.UTC) - datetime.timedelta(
        days=cutoff_days
    )

    if session is not None:
        return await _execute_deactivation(session, cutoff_date, user_ids)

    async with get_task_session() as session:
        return await _execute_deactivation(session, cutoff_date, user_ids)


async def _execute_deactivation(
    session: AsyncSession,
    cutoff_date: datetime.datetime,
    user_ids: list[int] | None,
) -> int:
    stmt = (
        update(UserModel)
        .where(
            UserModel.is_active == True,  # noqa: E712
            UserModel.is_admin == False,  # noqa: E712
            or_(
                UserModel.last_login_at < cutoff_date,
                and_(
                    UserModel.last_login_at.is_(None),
                    UserModel.created_at < cutoff_date,
                ),
            ),
        )
        .values(is_active=False)
    )

    if user_ids:
        stmt = stmt.where(UserModel.id.in_(user_ids))

    result = await session.execute(stmt)
    # sqlalchemy CursorResult has rowcount, but typing might not see it on Result
    return result.rowcount  # type: ignore[attr-defined]
