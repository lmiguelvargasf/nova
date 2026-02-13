from collections.abc import AsyncIterator, Awaitable, Callable

import pytest
from advanced_alchemy.extensions.litestar import SQLAlchemyAsyncConfig
from argon2 import PasswordHasher
from litestar import Litestar
from litestar.testing import AsyncTestClient

from backend.application import create_app
from backend.apps import models as app_models
from backend.apps.users.models import UserModel
from backend.auth.jwt import jwt_auth
from backend.config.alchemy import build_connection_string, session_config
from backend.config.base import settings

type UserFactory = Callable[..., Awaitable[UserModel]]


@pytest.fixture
def create_user(db_sessionmaker) -> UserFactory:
    async def _create_user(
        *,
        email: str,
        password: str = "SecurePassword123!",
        first_name: str = "Test",
        last_name: str = "User",
        is_admin: bool = False,
        is_active: bool = True,
    ) -> UserModel:
        async with db_sessionmaker() as session:
            ph = PasswordHasher()
            user_model = UserModel(
                email=email,
                password_hash=ph.hash(password),
                first_name=first_name,
                last_name=last_name,
                is_admin=is_admin,
                is_active=is_active,
            )
            session.add(user_model)
            await session.commit()
            await session.refresh(user_model)
            return user_model

    return _create_user


@pytest.fixture
async def user(create_user: UserFactory) -> UserModel:
    return await create_user(email="user@example.com")


@pytest.fixture
async def other_user(create_user: UserFactory) -> UserModel:
    return await create_user(email="other@example.com")


@pytest.fixture
async def rest_client(
    db_schema: None,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[AsyncTestClient[Litestar]]:
    async def retrieve_user_handler(token, _connection):
        try:
            user_id = int(token.sub)
        except TypeError, ValueError:
            return None
        return UserModel(id=user_id)

    monkeypatch.setattr(jwt_auth, "retrieve_user_handler", retrieve_user_handler)
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
