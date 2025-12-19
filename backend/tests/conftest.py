from collections.abc import AsyncIterator
from typing import Any

import pytest
from litestar import Litestar, get
from litestar.testing import AsyncTestClient
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.litestar import make_graphql_controller

from backend.schema import schema


@pytest.fixture
def db_session_mock(mocker) -> AsyncSession:
    session = mocker.Mock(spec=AsyncSession)
    session.scalar = mocker.AsyncMock()
    session.flush = mocker.AsyncMock()
    session.add = mocker.Mock()
    return session


@pytest.fixture(scope="function")
async def test_client(
    db_session_mock: AsyncSession,
) -> AsyncIterator[AsyncTestClient[Litestar]]:
    async def context_getter() -> dict[str, object]:
        return {"db_session": db_session_mock}

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
