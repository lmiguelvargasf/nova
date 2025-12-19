from backend.apps.users.models import UserModel


class TestUserQueries:
    async def test_get_user_by_id(self, db_session_mock, graphql_client):
        mock_user = UserModel(
            email="test@example.com",
            password_hash="hashed",
            first_name="Test",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        mock_user.id = 1
        db_session_mock.scalar.return_value = mock_user

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

        db_session_mock.scalar.assert_called_once()

    async def test_get_user_by_id_not_found(self, db_session_mock, graphql_client):
        db_session_mock.scalar.return_value = None

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
        db_session_mock.scalar.assert_called_once()
