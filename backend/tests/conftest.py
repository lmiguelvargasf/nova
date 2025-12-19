from collections.abc import AsyncIterator
from typing import Any

import pytest
from litestar import Litestar, get
from litestar.testing import AsyncTestClient
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from strawberry.litestar import make_graphql_controller

from backend.apps.users.services import UserService
from backend.config.alchemy import build_connection_string
from backend.config.base import settings
from backend.schema import schema


@pytest.fixture
async def db_engine() -> AsyncIterator[AsyncEngine]:
    if settings.postgres_test_db == settings.postgres_db:
        raise RuntimeError("Refusing to run tests against the development database.")

    engine = create_async_engine(
        build_connection_string(use_test_db=True),
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
    session.rollback = mocker.AsyncMock()
    return session


@pytest.fixture
def user_service_mock(mocker) -> UserService:
    service = mocker.Mock()
    service.get = mocker.AsyncMock()
    service.get_one_or_none = mocker.AsyncMock()
    service.create = mocker.AsyncMock()
    return service


@pytest.fixture(scope="function")
async def test_client(
    db_session_mock: AsyncSession,
    user_service_mock: UserService,
) -> AsyncIterator[AsyncTestClient[Litestar]]:
    async def context_getter() -> dict[str, object]:
        return {
            "db_session": db_session_mock,
            "user_service": user_service_mock,
        }

    GraphQLController = make_graphql_controller(
        schema=schema,
        path="/graphql",
        context_getter=context_getter,
    )

    class HealthStatus(BaseModel):
        status: str

    @get("/health")
    async def health_check() -> HealthStatus:
        return HealthStatus(status="ok")

    test_app = Litestar(route_handlers=[health_check, GraphQLController])

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
