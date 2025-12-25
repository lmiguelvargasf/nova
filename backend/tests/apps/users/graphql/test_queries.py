from advanced_alchemy.exceptions import NotFoundError

from backend.apps.users.models import UserModel


class TestUserQueries:
    async def test_get_user_by_id(
        self, user_service_mock, graphql_client, current_user_mock
    ):
        mock_user = UserModel(
            email="test@example.com",
            password_hash="hashed",
            first_name="Test",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        mock_user.id = 1
        user_service_mock.get.return_value = mock_user

        # Simulate authenticated user
        current_user_mock.id = 1
        current_user_mock.email = "test@example.com"

        query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                firstName
                lastName
                email
            }
        }
        """

        result = await graphql_client.query(query, variables={"id": "1"})

        assert "errors" not in result
        assert "data" in result

        user_data = result["data"]["user"]
        assert user_data is not None
        expected_data = {
            "id": "1",
            "firstName": "Test",
            "lastName": "User",
            "email": "test@example.com",
        }
        assert user_data == expected_data

        user_service_mock.get.assert_called_once_with(1)

    async def test_get_user_by_id_not_found(
        self, user_service_mock, graphql_client, current_user_mock
    ):
        user_service_mock.get.side_effect = NotFoundError(
            "No item found when one was expected"
        )

        # Simulate authenticated user
        current_user_mock.id = 1

        query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                email
            }
        }
        """

        result = await graphql_client.query(query, variables={"id": "999"})

        assert "errors" in result
        assert len(result["errors"]) == 1
        assert "User with id 999 not found" in result["errors"][0]["message"]
        user_service_mock.get.assert_called_once_with(999)

    async def test_get_user_unauthenticated(
        self, user_service_mock, graphql_client, current_user_mock
    ):
        # Simulate unauthenticated user
        current_user_mock.id = None

        query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                email
            }
        }
        """

        result = await graphql_client.query(query, variables={"id": "1"})

        assert "errors" in result
        assert result["errors"][0]["message"] == "User is not authenticated"
