from piccolo.apps.user.tables import BaseUser


class TestUserQueries:
    async def test_get_user_by_id(self, mocker, graphql_client):
        mock_objects = mocker.patch.object(BaseUser, "objects")
        mock_user = BaseUser(
            id=1,
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )
        mock_objects.return_value.get = mocker.AsyncMock(return_value=mock_user)

        query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                username
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
            "username": "testuser",
            "firstName": "Test",
            "lastName": "User",
            "email": "test@example.com",
        }
        assert user_data == expected_data

        mock_objects.return_value.get.assert_called_once()

    async def test_get_user_by_id_not_found(self, mocker, graphql_client):
        mock_objects = mocker.patch.object(BaseUser, "objects")
        mock_objects.return_value.get = mocker.AsyncMock(return_value=None)

        query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                username
            }
        }
        """

        result = await graphql_client.query(query, variables={"id": "999"})

        assert "errors" in result
        assert len(result["errors"]) == 1
        assert "User with id 999 not found" in result["errors"][0]["message"]
        mock_objects.return_value.get.assert_called_once()
