import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_429_TOO_MANY_REQUESTS

from backend.auth.jwt import jwt_auth


@pytest.mark.asyncio
async def test_rate_limit_path_exclusion(test_client):
    for _ in range(15):
        response = await test_client.get("/health")
        assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_rate_limit_anonymous_exceeds_limit(test_client):
    for _ in range(10):
        await test_client.get("/api/users/me")

    response = await test_client.get("/api/users/me")
    assert response.status_code == HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_rate_limit_authenticated(test_client):
    token = jwt_auth.create_token(identifier="1")
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(15):
        response = await test_client.get("/api/users/me", headers=headers)
        assert response.status_code in (HTTP_200_OK, 401)
