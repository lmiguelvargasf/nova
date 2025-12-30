import asyncio
import datetime

from celery.app.task import Task
from celery.utils.log import get_task_logger
from sqlalchemy import and_, or_, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.apps.users.models import UserModel
from backend.celery_app import app, get_task_session

logger = get_task_logger(__name__)


@app.task(
    bind=True,
    autoretry_for=(DBAPIError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def deactivate_inactive_users(
    self: Task,
    cutoff_days: int = 7,
    user_ids: list[int] | None = None,
) -> int:
    task_id = getattr(self.request, "id", None)
    logger.info(
        "deactivate_inactive_users start task_id=%s cutoff_days=%s user_ids_count=%s",
        task_id,
        cutoff_days,
        len(user_ids) if user_ids else None,
    )
    count = asyncio.run(_deactivate_inactive_users_async(cutoff_days, user_ids))
    logger.info("deactivate_inactive_users done task_id=%s updated=%s", task_id, count)
    return count


async def _deactivate_inactive_users_async(
    cutoff_days: int,
    user_ids: list[int] | None = None,
    *,
    session: AsyncSession | None = None,
) -> int:
    cutoff_date = datetime.datetime.now(datetime.UTC) - datetime.timedelta(
        days=cutoff_days
    )

    async def _run(session: AsyncSession) -> int:
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

    if session is not None:
        return await _run(session)

    async with get_task_session() as session:
        return await _run(session)
