import asyncio
import datetime

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.apps.users.models import UserModel
from backend.celery_app import app
from backend.config.alchemy import alchemy_config
from backend.config.base import settings


@app.task
def deactivate_inactive_users(
    cutoff_days: int | None = None,
    user_ids: list[int] | None = None,
) -> int:
    if cutoff_days is None:
        cutoff_days = settings.celery_inactive_cutoff_days

    return asyncio.run(_deactivate_inactive_users_async(cutoff_days, user_ids))


async def _deactivate_inactive_users_async(
    cutoff_days: int,
    user_ids: list[int] | None = None,
) -> int:
    cutoff_date = datetime.datetime.now(datetime.UTC) - datetime.timedelta(
        days=cutoff_days
    )

    engine = alchemy_config.get_engine()

    async with AsyncSession(engine) as session, session.begin():
        stmt = (
            update(UserModel)
            .where(
                UserModel.is_active == True,  # noqa: E712
                UserModel.last_login_at < cutoff_date,
                UserModel.last_login_at.is_not(None),
                UserModel.is_admin == False,  # noqa: E712
            )
            .values(is_active=False)
        )

        if user_ids:
            stmt = stmt.where(UserModel.id.in_(user_ids))

        result = await session.execute(stmt)
        # sqlalchemy CursorResult has rowcount, but typing might not see it on Result
        return result.rowcount  # type: ignore[attr-defined]
