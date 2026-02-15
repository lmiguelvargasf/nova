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
from backend.config.alchemy import build_connection_string, session_config


class DevelopmentDatabaseError(RuntimeError):
    def __init__(self) -> None:
        super().__init__("Refusing to run tests against the development database.")


@pytest.fixture
async def db_engine() -> AsyncIterator[AsyncEngine]:
    from backend.config.alchemy import build_connection_string
    from backend.config.base import settings

    if settings.postgres_test_db == settings.postgres_db:
        raise DevelopmentDatabaseError

    engine = create_async_engine(
        build_connection_string(db_name=settings.postgres_test_db),
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
async def test_client(db_schema: None) -> AsyncIterator[AsyncTestClient[Litestar]]:
    from backend.config.base import settings

    config = SQLAlchemyAsyncConfig(
        connection_string=build_connection_string(db_name=settings.postgres_test_db),
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
