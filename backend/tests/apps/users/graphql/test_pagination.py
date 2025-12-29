from strawberry.relay.utils import to_base64

from backend.apps.users.models import UserModel


class TestUserPagination:
    async def test_users_pagination(
        self,
        user_service_mock,
        graphql_client,
        mocker,
    ):
        # Setup mock data
        users = []
        for i in range(5):
            u = UserModel(
                email=f"user{i}@example.com",
                password_hash="hashed",
                first_name=f"First{i}",
                last_name=f"Last{i}",
            )
            u.id = i + 1
            users.append(u)

        user_service_mock.list = mocker.AsyncMock(return_value=users)

        query = """
        query GetUsers {
            users(first: 3) {
                edges {
                    node {
                        id
                        email
                    }
                }
                pageInfo {
                    hasNextPage
                }
            }
        }
        """

        result = await graphql_client.query(query)

        assert "errors" not in result
        data = result["data"]["users"]
        assert len(data["edges"]) == 3
        assert data["pageInfo"]["hasNextPage"] is True
        assert data["edges"][0]["node"]["email"] == "user0@example.com"

        # Check ID format (Global ID)
        first_id = data["edges"][0]["node"]["id"]
        assert first_id != "1"
        assert to_base64("UserType", "1") == first_id

    async def test_node_query(
        self,
        user_service_mock,
        graphql_client,
        mocker,
    ):
        mock_user = UserModel(
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )
        mock_user.id = 1

        # list() is called by resolve_nodes with id__in=[1]
        user_service_mock.list = mocker.AsyncMock(return_value=[mock_user])

        # Calculate expected Global ID
        global_id = to_base64("UserType", "1")

        query = """
        query GetNode($id: ID!) {
            node(id: $id) {
                id
                ... on UserType {
                    email
                }
            }
        }
        """

        result = await graphql_client.query(query, variables={"id": global_id})

        assert "errors" not in result
        data = result["data"]["node"]
        assert data["id"] == global_id
        assert data["email"] == "test@example.com"

        # Verify user_service.list was called
        user_service_mock.list.assert_called_once()
        call_kwargs = user_service_mock.list.call_args.kwargs
        assert call_kwargs.get("id__in") == [1]
