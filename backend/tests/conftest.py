from collections.abc import AsyncIterator
from typing import Any

import pytest
from litestar import Litestar
from litestar.testing import AsyncTestClient

from backend import app


@pytest.fixture(scope="function")
async def test_client() -> AsyncIterator[AsyncTestClient[Litestar]]:
    async with AsyncTestClient(app=app) as client:
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
