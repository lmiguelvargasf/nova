from collections.abc import AsyncIterator

import pytest
from advanced_alchemy.extensions.litestar import SQLAlchemyAsyncConfig
from litestar import Litestar
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.application import create_app
from backend.apps import models as app_models
from backend.apps.users.models import UserModel
from backend.auth.jwt import jwt_auth
from backend.config.alchemy import build_connection_string, session_config
from backend.config.base import settings


class DevelopmentDatabaseError(RuntimeError):
    def __init__(self) -> None:
        super().__init__("Refusing to run tests against the development database.")


def _test_db_name(main_db_name: str) -> str:
    return f"{main_db_name}_test"


@pytest.fixture
async def db_engine() -> AsyncIterator[AsyncEngine]:
    test_db_name = _test_db_name(settings.postgres_db)
    if test_db_name == settings.postgres_db:
        raise DevelopmentDatabaseError

    engine = create_async_engine(
        build_connection_string(db_name=test_db_name),
        pool_pre_ping=True,
    )

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def db_schema(db_engine: AsyncEngine) -> AsyncIterator[None]:
    async with db_engine.begin() as conn:
        await conn.run_sync(app_models.metadata.drop_all)
        await conn.run_sync(app_models.metadata.create_all)
    try:
        yield
    finally:
        async with db_engine.begin() as conn:
            await conn.run_sync(app_models.metadata.drop_all)


@pytest.fixture
async def db_sessionmaker(db_engine: AsyncEngine, db_schema: None):
    return async_sessionmaker(db_engine, expire_on_commit=False)


@pytest.fixture
async def db_session(db_sessionmaker: async_sessionmaker[AsyncSession]):
    async with db_sessionmaker() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture
async def test_client(
    db_schema: None,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[AsyncTestClient[Litestar]]:
    async def retrieve_user_handler(token, _connection):
        try:
            user_id = int(token.sub)
        except (TypeError, ValueError):
            return None
        return UserModel(id=user_id)

    monkeypatch.setattr(jwt_auth, "retrieve_user_handler", retrieve_user_handler)
    test_db_name = _test_db_name(settings.postgres_db)
    config = SQLAlchemyAsyncConfig(
        connection_string=build_connection_string(db_name=test_db_name),
        session_config=session_config,
        metadata=app_models.metadata,
        create_all=False,
    )
    app = create_app(
        use_sqlalchemy_plugin=True,
        enable_admin=False,
        alchemy_config_override=config,
    )
    async with AsyncTestClient(app=app) as client:
        yield client
