from strawberry.relay.utils import to_base64

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
            "id": to_base64("UserType", "1"),
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

    async def test_get_user_by_global_id(
        self,
        user_service_mock,
        graphql_client,
        mocker,
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

        user_service_mock.list = mocker.AsyncMock(return_value=[mock_user])

        query = """
        query GetUserById($id: ID!) {
            userById(id: $id) {
                id
                firstName
                lastName
                email
            }
        }
        """

        global_id = to_base64("UserType", "1")
        result = await graphql_client.query(query, variables={"id": global_id})

        assert "errors" not in result
        assert result["data"]["userById"] == {
            "id": global_id,
            "firstName": "Test",
            "lastName": "User",
            "email": "test@example.com",
        }

        user_service_mock.list.assert_called_once()
        assert user_service_mock.list.call_args.kwargs.get("id__in") == [1]

    async def test_get_user_by_global_id_unauthenticated(
        self,
        graphql_client,
        current_user_mock,
    ):
        current_user_mock.id = None

        query = """
        query GetUserById($id: ID!) {
            userById(id: $id) {
                id
            }
        }
        """

        global_id = to_base64("UserType", "1")
        result = await graphql_client.query(query, variables={"id": global_id})

        assert "errors" in result
        assert result["errors"][0]["message"] == "User is not authenticated"

    async def test_get_user_by_global_id_not_found(
        self,
        user_service_mock,
        graphql_client,
        mocker,
    ):
        user_service_mock.list = mocker.AsyncMock(return_value=[])

        query = """
        query GetUserById($id: ID!) {
            userById(id: $id) {
                id
            }
        }
        """

        global_id = to_base64("UserType", "999")
        result = await graphql_client.query(query, variables={"id": global_id})

        assert "errors" in result
        assert result["errors"][0]["message"] == "User not found"

    # Note: legacy `user(id: ID!)` query was removed in favor of Relay Global IDs.
