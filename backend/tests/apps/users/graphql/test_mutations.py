from backend.apps.users.models import UserModel


class TestUserMutations:
    async def test_create_user_success(self, db_session_mock, graphql_client):
        db_session_mock.scalar.return_value = None

        created: list[UserModel] = []

        def add_side_effect(obj):
            created.append(obj)

        async def flush_side_effect():
            created[0].id = 1

        db_session_mock.add.side_effect = add_side_effect
        db_session_mock.flush.side_effect = flush_side_effect

        mutation = """
        mutation CreateUser($userInput: UserInput!) {
            createUser(userInput: $userInput) {
                id
                firstName
                lastName
                email
            }
        }
        """
        variables = {
            "userInput": {
                "email": "new@example.com",
                "password": "TestPassword123",
                "firstName": "New",
                "lastName": "User",
            }
        }
        result = await graphql_client.mutation(mutation, variables=variables)

        assert "data" in result
        assert "createUser" in result["data"]
        expected_user_data = {
            "id": "1",
            "firstName": "New",
            "lastName": "User",
            "email": "new@example.com",
        }
        assert result["data"]["createUser"] == expected_user_data

        db_session_mock.scalar.assert_called_once()
        db_session_mock.add.assert_called_once()
        db_session_mock.flush.assert_called_once()

    async def test_create_user_already_exists(self, db_session_mock, graphql_client):
        existing_user = UserModel(
            email="existing@example.com",
            password_hash="hashed",
            first_name="Existing",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        existing_user.id = 1
        db_session_mock.scalar.return_value = existing_user

        mutation = """
        mutation CreateUser($userInput: UserInput!) {
            createUser(userInput: $userInput) {
                id
                email
            }
        }
        """

        variables = {
            "userInput": {
                "email": "existing@example.com",
                "password": "TestPassword123",
                "firstName": "Test",
                "lastName": "User",
            }
        }

        result = await graphql_client.mutation(mutation, variables=variables)

        assert "errors" in result
        assert len(result["errors"]) == 1
        assert (
            "User with email 'existing@example.com' already exists"
            in result["errors"][0]["message"]
        )

        db_session_mock.scalar.assert_called_once()
