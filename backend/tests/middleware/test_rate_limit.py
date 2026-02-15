import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_429_TOO_MANY_REQUESTS

from backend.auth.jwt import jwt_auth

pytestmark = pytest.mark.unit
INTROSPECTION_QUERY = {"query": "{ __schema { queryType { name } } }"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "count", "payload"),
    [
        ("/health", 15, None),
        ("/graphql", 10, INTROSPECTION_QUERY),
    ],
    ids=["health-path-excluded", "graphql-anon-within-limit"],
)
async def test_rate_limit_allows_expected_requests(test_client, path, count, payload):
    for _ in range(count):
        if payload is None:
            response = await test_client.get(path)
        else:
            response = await test_client.post(path, json=payload)
        assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_rate_limit_anonymous_exceeds_limit(test_client):
    for _ in range(10):
        await test_client.post("/graphql", json=INTROSPECTION_QUERY)

    response = await test_client.post("/graphql", json=INTROSPECTION_QUERY)
    assert response.status_code == HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_rate_limit_authenticated(test_client):
    token = jwt_auth.create_token(identifier="1")
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(15):
        response = await test_client.post(
            "/graphql",
            json=INTROSPECTION_QUERY,
            headers=headers,
        )
        assert response.status_code == HTTP_200_OK
