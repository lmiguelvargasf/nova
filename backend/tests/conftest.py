from collections.abc import AsyncIterator
from typing import Any

import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.testing import AsyncTestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.application import create_app
from backend.apps.users.models import UserModel
from backend.apps.users.services import UserService
from backend.graphql.context import GraphQLContext, Services


class DevelopmentDatabaseError(RuntimeError):
    def __init__(self) -> None:
        super().__init__("Refusing to run tests against the development database.")


class InvalidTestDatabaseNameError(RuntimeError):
    def __init__(self, db_name: str) -> None:
        super().__init__(f"Unsafe test database name generated: {db_name}")


def _validate_test_db_name(db_name: str) -> str:
    if not db_name.replace("_", "").isalnum():
        raise InvalidTestDatabaseNameError(db_name)
    return db_name


def _test_db_name_for_worker(base_name: str, worker_id: str) -> str:
    safe_worker = worker_id.replace("-", "_")
    return _validate_test_db_name(f"{base_name}_{safe_worker}")


def _base_test_db_name(main_db_name: str) -> str:
    return _validate_test_db_name(f"{main_db_name}_test")


@pytest.fixture(scope="session")
def test_db_name(worker_id: str) -> str:
    from backend.config.base import settings

    base_test_db_name = _base_test_db_name(settings.postgres_db)
    if base_test_db_name == settings.postgres_db:
        raise DevelopmentDatabaseError
    return _test_db_name_for_worker(base_test_db_name, worker_id)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def worker_test_database(test_db_name: str) -> AsyncIterator[str]:
    from backend.config.alchemy import build_connection_string
    from backend.config.base import settings

    admin_engine = create_async_engine(
        build_connection_string(db_name=settings.postgres_db),
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )

    async with admin_engine.connect() as conn:
        exists = await conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
            {"db_name": test_db_name},
        )
        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{test_db_name}"'))

    try:
        yield test_db_name
    finally:
        async with admin_engine.connect() as conn:
            await conn.execute(
                text(
                    """
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = :db_name
                      AND pid <> pg_backend_pid()
                    """
                ),
                {"db_name": test_db_name},
            )
            await conn.execute(text(f'DROP DATABASE IF EXISTS "{test_db_name}"'))
        await admin_engine.dispose()


@pytest.fixture
async def db_engine(worker_test_database: str) -> AsyncIterator[AsyncEngine]:
    from backend.config.alchemy import build_connection_string

    engine = create_async_engine(
        build_connection_string(db_name=worker_test_database),
        pool_pre_ping=True,
    )
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def db_schema(db_engine: AsyncEngine) -> AsyncIterator[None]:
    from backend.apps import models as app_models

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
def db_session_mock(mocker) -> AsyncSession:
    session = mocker.Mock(spec=AsyncSession)
    session.scalar = mocker.AsyncMock()
    session.flush = mocker.AsyncMock()
    session.add = mocker.Mock()
    session.commit = mocker.AsyncMock()
    session.rollback = mocker.AsyncMock()
    return session


@pytest.fixture
def user_service_mock(mocker) -> UserService:
    service = mocker.Mock()
    service.get = mocker.AsyncMock()
    service.get_one_or_none = mocker.AsyncMock()
    service.create = mocker.AsyncMock()
    service.create_user_account = mocker.AsyncMock()
    service.authenticate_for_login = mocker.AsyncMock()
    service.apply_user_updates = mocker.AsyncMock()
    service.soft_delete_user = mocker.AsyncMock()
    service.get_authenticated_user = mocker.AsyncMock()
    return service


@pytest.fixture
def current_user_mock(mocker):
    user = mocker.Mock(spec=UserModel)
    user.id = 1
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"
    user.password_hash = "hashed"
    return user


@pytest.fixture
async def test_client(
    db_session_mock: AsyncSession,
    user_service_mock: UserService,
    current_user_mock,
) -> AsyncIterator[AsyncTestClient[Litestar]]:
    async def context_getter() -> GraphQLContext:
        services = Services(db_session_mock)
        services.users = user_service_mock
        return GraphQLContext(
            db_session=db_session_mock,
            services=services,
            user=current_user_mock if current_user_mock.id else None,
        )

    test_app = create_app(
        graphql_context_getter=context_getter,
        use_sqlalchemy_plugin=False,
        enable_admin=False,
    )

    async with AsyncTestClient(app=test_app) as client:
        yield client


class GraphQLClient:
    def __init__(self, client):
        self.client = client
        self.endpoint = "/graphql"

    async def query(self, query_string: str, variables: dict[str, Any] | None = None):
        """Execute a GraphQL query with variables"""
        payload: dict[str, Any] = {"query": query_string}
        if variables:
            payload["variables"] = variables

        response = await self.client.post(self.endpoint, json=payload)
        return response.json()

    async def mutation(
        self, mutation_string: str, variables: dict[str, Any] | None = None
    ):
        """Execute a GraphQL mutation with variables"""
        return await self.query(mutation_string, variables)


@pytest.fixture
def graphql_client(test_client):
    """Provides a GraphQL client for testing"""
    return GraphQLClient(test_client)
