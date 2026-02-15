import pytest
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_429_TOO_MANY_REQUESTS,
)


@pytest.mark.asyncio
async def test_rate_limit_path_exclusion(test_client):
    for _ in range(15):
        response = await test_client.get("/health")
        assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_rate_limit_anonymous_exceeds_limit(test_client):
    for i in range(10):
        response = await test_client.post(
            "/api/auth/register",
            json={
                "email": f"rate-limit-{i}@example.com",
                "password": "SecurePassword123!",
                "first_name": "Rate",
                "last_name": "Limit",
            },
        )
        assert response.status_code == HTTP_201_CREATED

    response = await test_client.post(
        "/api/auth/register",
        json={
            "email": "rate-limit-overflow@example.com",
            "password": "SecurePassword123!",
            "first_name": "Rate",
            "last_name": "Limit",
        },
    )
    assert response.status_code == HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_rate_limit_authenticated(test_client):
    register_response = await test_client.post(
        "/api/auth/register",
        json={
            "email": "auth-rate-limit@example.com",
            "password": "SecurePassword123!",
            "first_name": "Auth",
            "last_name": "User",
        },
    )
    assert register_response.status_code == HTTP_201_CREATED
    token = register_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(15):
        response = await test_client.get("/api/users/me", headers=headers)
        assert response.status_code == HTTP_200_OK
