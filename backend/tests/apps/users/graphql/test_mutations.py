from piccolo.apps.user.tables import BaseUser


class TestUserMutations:
    async def test_create_user_success(self, mocker, graphql_client):
        # Setup mock to return no existing user
        mock_objects = mocker.patch.object(BaseUser, "objects")
        mock_get = mocker.AsyncMock(return_value=None)
        mock_objects.return_value.get = mock_get

        mock_save = mocker.patch.object(BaseUser, "save", new_callable=mocker.AsyncMock)
        original_init = BaseUser.__init__

        def patched_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self.id = 1

        mocker.patch.object(BaseUser, "__init__", patched_init)

        mutation = """
        mutation CreateUser($userInput: UserInput!) {
            createUser(userInput: $userInput) {
                id
                username
                firstName
                lastName
                email
            }
        }
        """
        variables = {
            "userInput": {
                "username": "newuser",
                "firstName": "New",
                "lastName": "User",
                "email": "new@example.com",
            }
        }
        result = await graphql_client.mutation(mutation, variables=variables)

        assert "data" in result
        assert "createUser" in result["data"]
        expected_user_data = {
            "id": "1",
            "username": "newuser",
            "firstName": "New",
            "lastName": "User",
            "email": "new@example.com",
        }
        assert result["data"]["createUser"] == expected_user_data

        mock_get.assert_called_once()
        mock_save.assert_called_once()

    async def test_create_user_already_exists(self, mocker, graphql_client):
        mock_objects = mocker.patch.object(BaseUser, "objects")
        existing_user = BaseUser(
            id=1,
            username="existinguser",
            first_name="Existing",
            last_name="User",
            email="existing@example.com",
        )
        mock_objects.return_value.get = mocker.AsyncMock(return_value=existing_user)

        mutation = """
        mutation CreateUser($userInput: UserInput!) {
            createUser(userInput: $userInput) {
                id
                username
            }
        }
        """

        variables = {
            "userInput": {
                "username": "existinguser",
                "firstName": "Test",
                "lastName": "User",
                "email": "test@example.com",
            }
        }

        result = await graphql_client.mutation(mutation, variables=variables)

        assert "errors" in result
        assert len(result["errors"]) == 1
        assert (
            "User with username 'existinguser' already exists"
            in result["errors"][0]["message"]
        )

        mock_objects.return_value.get.assert_called_once()
