import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.apps.users.models import UserModel
from backend.apps.users.tasks import _deactivate_inactive_users_async


@pytest.mark.asyncio
async def test_deactivate_inactive_users(
    db_engine, db_session: AsyncSession, monkeypatch
):
    from backend.config import alchemy

    # Patch alchemy_config.get_engine to return the test db_engine
    monkeypatch.setattr(alchemy.alchemy_config, "get_engine", lambda: db_engine)

    # Setup data
    cutoff_days = 7
    now = datetime.datetime.now(datetime.UTC)

    # User 1: Inactive (should stay inactive)
    user1 = UserModel(
        email="inactive@example.com",
        password_hash="hash",
        first_name="Inactive",
        last_name="User",
        is_active=False,
    )

    # User 2: Active, logged in recently (should stay active)
    user2 = UserModel(
        email="active_recent@example.com",
        password_hash="hash",
        first_name="Active",
        last_name="Recent",
        is_active=True,
        last_login_at=now,
    )

    # User 3: Active, logged in long ago (should be deactivated)
    user3 = UserModel(
        email="active_old@example.com",
        password_hash="hash",
        first_name="Active",
        last_name="Old",
        is_active=True,
        last_login_at=now - datetime.timedelta(days=cutoff_days + 1),
    )

    # User 4: Admin, logged in long ago (should stay active)
    user4 = UserModel(
        email="admin_old@example.com",
        password_hash="hash",
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_admin=True,
        last_login_at=now - datetime.timedelta(days=cutoff_days + 1),
    )

    db_session.add_all([user1, user2, user3, user4])
    await db_session.commit()

    # Run task
    count = await _deactivate_inactive_users_async(cutoff_days, engine=db_engine)

    assert count == 1

    # Verify
    # Refresh objects from DB
    await db_session.refresh(user1)
    await db_session.refresh(user2)
    await db_session.refresh(user3)
    await db_session.refresh(user4)

    assert user1.is_active is False
    assert user2.is_active is True
    assert user3.is_active is False
    assert user4.is_active is True
