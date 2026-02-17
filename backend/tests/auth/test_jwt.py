import pytest
from advanced_alchemy.extensions.litestar import SQLAlchemyAsyncConfig
from argon2 import PasswordHasher
from litestar.status_codes import HTTP_200_OK
from litestar.testing import AsyncTestClient

from backend.application import create_app
from backend.apps import models as app_models
from backend.apps.users.models import UserModel
from backend.auth.jwt import jwt_auth
from backend.config.alchemy import build_connection_string, session_config


@pytest.mark.asyncio
async def test_jwt_auth_allows_me_endpoint(
    db_schema: None,
    test_db_name: str,
    db_sessionmaker,
) -> None:
    async with db_sessionmaker() as session:
        ph = PasswordHasher()
        user = UserModel(
            email="jwt@example.com",
            password_hash=ph.hash("SecurePassword123!"),
            first_name="Jwt",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    token = jwt_auth.create_token(identifier=str(user.id))
    config = SQLAlchemyAsyncConfig(
        connection_string=build_connection_string(db_name=test_db_name),
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
        response = await client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == HTTP_200_OK
    assert response.json()["email"] == "jwt@example.com"
