from collections.abc import AsyncIterator

import pytest
from advanced_alchemy.extensions.litestar import SQLAlchemyAsyncConfig
from litestar import Litestar
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
from litestar.testing import AsyncTestClient
from sqlalchemy import select

from backend.application import create_app
from backend.apps import models as app_models
from backend.apps.users.models import UserModel
from backend.config.alchemy import build_connection_string, session_config
from backend.config.base import settings


@pytest.fixture
async def rest_client(
    db_schema: None,
) -> AsyncIterator[AsyncTestClient[Litestar]]:
    config = SQLAlchemyAsyncConfig(
        connection_string=build_connection_string(db_name=settings.postgres_test_db),
        session_config=session_config,
        metadata=app_models.metadata,
        create_all=False,
    )
    test_app = create_app(
        use_sqlalchemy_plugin=True,
        enable_admin=False,
        alchemy_config_override=config,
    )
    async with AsyncTestClient(app=test_app) as client:
        yield client


async def test_rest_soft_delete_reactivates_user(
    rest_client: AsyncTestClient[Litestar],
    db_sessionmaker,
) -> None:
    payload = {
        "email": "rest@example.com",
        "password": "SecurePassword123!",
        "first_name": "Rest",
        "last_name": "User",
    }
    register_response = await rest_client.post(
        "/api/auth/register",
        json=payload,
    )
    assert register_response.status_code == HTTP_201_CREATED
    register_data = register_response.json()
    token = register_data["token"]
    assert register_data["reactivated"] is False
    assert register_data["user"]["email"] == payload["email"]

    headers = {"Authorization": f"Bearer {token}"}
    me_response = await rest_client.get("/api/users/me", headers=headers)
    assert me_response.status_code == HTTP_200_OK
    assert me_response.json()["email"] == payload["email"]

    delete_response = await rest_client.delete("/api/users/me", headers=headers)
    assert delete_response.status_code == HTTP_200_OK
    assert delete_response.json() == {"deleted": True}

    async with db_sessionmaker() as session:
        user = await session.scalar(
            select(UserModel).where(UserModel.email == payload["email"])
        )
        assert user is not None
        assert user.deleted_at is not None

    login_response = await rest_client.post(
        "/api/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login_response.status_code == HTTP_201_CREATED
    login_data = login_response.json()
    assert login_data["reactivated"] is True
    assert login_data["token"]

    async with db_sessionmaker() as session:
        user = await session.scalar(
            select(UserModel).where(UserModel.email == payload["email"])
        )
        assert user is not None
        assert user.deleted_at is None
