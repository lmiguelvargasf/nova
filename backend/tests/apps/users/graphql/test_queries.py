from advanced_alchemy.exceptions import NotFoundError

from backend.apps.users.models import UserModel


class TestUserQueries:
    async def test_me(self, graphql_client, current_user_mock, user_service_mock):
        query = """
        query Me {
            me {
                id
                firstName
                lastName
                email
            }
        }
        """

        result = await graphql_client.query(query)

        assert "errors" not in result
        assert "data" in result
        me_data = result["data"]["me"]
        assert me_data == {
            "id": "1",
            "firstName": "Test",
            "lastName": "User",
            "email": "test@example.com",
        }
        user_service_mock.get.assert_not_called()

    async def test_me_unauthenticated(self, graphql_client, current_user_mock):
        current_user_mock.id = None

        query = """
        query Me {
            me {
                id
                email
            }
        }
        """

        result = await graphql_client.query(query)

        assert "errors" in result
        assert result["errors"][0]["message"] == "User is not authenticated"

    async def test_get_user_by_id(
        self,
        user_service_mock,
        graphql_client,
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

    async def test_get_user_unauthenticated(self, graphql_client, current_user_mock):
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

    async def test_users_connection(
        self,
        graphql_client,
        user_service_mock,
    ):
        first_user = UserModel(
            email="first@example.com",
            password_hash="hashed",
            first_name="First",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        first_user.id = 1
        second_user = UserModel(
            email="second@example.com",
            password_hash="hashed",
            first_name="Second",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        second_user.id = 2
        user_service_mock.list.return_value = [first_user, second_user]

        query = """
        query Users($first: Int) {
            users(first: $first) {
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

        result = await graphql_client.query(query, variables={"first": 1})

        assert "errors" not in result
        edges = result["data"]["users"]["edges"]
        assert len(edges) == 1
        assert edges[0]["node"]["email"] == "first@example.com"
        assert result["data"]["users"]["pageInfo"]["hasNextPage"] is True
        user_service_mock.list.assert_called_once()

    async def test_users_connection_unauthenticated(
        self,
        graphql_client,
        current_user_mock,
    ):
        current_user_mock.id = None

        query = """
        query Users {
            users {
                edges {
                    node {
                        id
                    }
                }
            }
        }
        """

        result = await graphql_client.query(query)

        assert "errors" in result
        assert result["errors"][0]["message"] == "User is not authenticated"
