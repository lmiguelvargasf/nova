import pytest


@pytest.mark.asyncio
async def test_query_depth_limit(graphql_client):
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
async def test_query_depth_allowed(graphql_client):
    query = """
    query {
      node(id: "VXNlclR5cGU6MQ==") {
        id
      }
    }
    """

    response = await graphql_client.query(query)
    if "errors" in response:
        assert not any(
            "exceeds maximum operation depth" in error["message"]
            for error in response["errors"]
        )
