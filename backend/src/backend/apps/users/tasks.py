import asyncio
import datetime

from sqlalchemy import and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from backend.apps.users.models import UserModel
from backend.celery_app import app
from backend.config.alchemy import build_connection_string
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
    cutoff_days = 5
    cutoff_date = datetime.datetime.now(datetime.UTC) - datetime.timedelta(
        days=cutoff_days
    )
    engine = create_async_engine(build_connection_string())

    try:
        async with AsyncSession(engine) as session, session.begin():
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
            return result.rowcount  # type: ignore[attr-defined]
    finally:
        await engine.dispose()
