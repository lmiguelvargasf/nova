import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_429_TOO_MANY_REQUESTS

from backend.auth.jwt import jwt_auth


@pytest.mark.asyncio
async def test_rate_limit_path_exclusion(test_client):
    # /health should be excluded from rate limiting
    for _ in range(15):
        response = await test_client.get("/health")
        assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_rate_limit_anonymous_within_limit(test_client):
    # /graphql should be rate limited (default 10 for anonymous)
    query = {"query": "{ __schema { queryType { name } } }"}

    # First 10 requests should pass
    for _ in range(10):
        response = await test_client.post("/graphql", json=query)
        assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_rate_limit_anonymous_exceeds_limit(test_client):
    # /graphql should be rate limited (default 10 for anonymous)
    query = {"query": "{ __schema { queryType { name } } }"}

    # Reach the limit
    for _ in range(10):
        await test_client.post("/graphql", json=query)

    # 11th request should be throttled
    response = await test_client.post("/graphql", json=query)
    assert response.status_code == HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_rate_limit_authenticated(test_client, mocker):
    # Mock settings to have a lower limit for testing if needed,
    # but 100 is still okay for a quick loop if we want to be thorough.
    # However, let's keep it 100 to test the actual config.

    token = jwt_auth.create_token(identifier="1")
    headers = {"Authorization": f"Bearer {token}"}
    query = {"query": "{ __schema { queryType { name } } }"}

    # We'll just test that it's higher than anonymous
    for _ in range(15):
        response = await test_client.post("/graphql", json=query, headers=headers)
        assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_graphql_query_depth_limit(graphql_client):
    # settings.graphql_max_depth is 10 by default.
    # We can test a very deep query (more than 10 levels)
    # Since we don't have deep models, we can use introspection or nested fragments
    # if allowed, or just repeat the same field if the schema allows it.

    # A simple way is to use a very deep nesting that doesn't necessarily exist
    # but will be caught by the parser/depth limiter before execution.

    deep_query = (
        "query { " + 'node(id: "VXNlclR5cGU6MQ==") { ' * 11 + "id" + " }" * 11 + " }"
    )

    response = await graphql_client.query(deep_query)

    assert "errors" in response
    assert any(
        "exceeds maximum operation depth" in error["message"]
        for error in response["errors"]
    )


@pytest.mark.asyncio
async def test_graphql_query_depth_allowed(graphql_client, mocker):
    # This query has depth 2 (Query -> user -> id) which is < 10
    query = """
    query {
      node(id: "VXNlclR5cGU6MQ==") {
        id
      }
    }
    """
    # Mocking user service to return a user so it doesn't fail on execution
    # though depth limiter should pass before this.

    response = await graphql_client.query(query)
    # If it passed depth check, it might still have errors (like NOT_FOUND),
    # but it shouldn't be a depth error.
    if "errors" in response:
        assert not any(
            "exceeds maximum operation depth" in error["message"]
            for error in response["errors"]
        )
