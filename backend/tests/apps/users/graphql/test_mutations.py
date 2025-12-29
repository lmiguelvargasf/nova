from strawberry.relay.utils import to_base64

from backend.apps.users.models import UserModel


class TestUserMutations:
    async def test_create_user_success(self, user_service_mock, graphql_client):
        mock_user = UserModel(
            email="new@example.com",
            password_hash="hashed",
            first_name="New",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        mock_user.id = 1
        user_service_mock.get_one_or_none.return_value = None
        user_service_mock.create.return_value = mock_user

        mutation = """
        mutation CreateUser($userInput: UserInput!) {
            createUser(userInput: $userInput) {
                token
                user {
                    id
                    firstName
                    lastName
                    email
                }
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
            "id": to_base64("UserType", "1"),
            "firstName": "New",
            "lastName": "User",
            "email": "new@example.com",
        }
        assert result["data"]["createUser"]["user"] == expected_user_data
        assert result["data"]["createUser"]["token"] is not None

        user_service_mock.get_one_or_none.assert_called_once_with(
            email="new@example.com"
        )
        user_service_mock.create.assert_called_once()
        create_call = user_service_mock.create.call_args
        data = create_call.args[0]
        assert data["email"] == "new@example.com"
        assert data["first_name"] == "New"
        assert data["last_name"] == "User"
        assert data["password_hash"] != "TestPassword123"
        assert create_call.kwargs["auto_commit"] is True

    async def test_create_user_already_exists(self, user_service_mock, graphql_client):
        existing_user = UserModel(
            email="existing@example.com",
            password_hash="hashed",
            first_name="Existing",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        existing_user.id = 1
        user_service_mock.get_one_or_none.return_value = existing_user

        mutation = """
        mutation CreateUser($userInput: UserInput!) {
            createUser(userInput: $userInput) {
                user {
                    id
                    email
                }
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

        user_service_mock.get_one_or_none.assert_called_once_with(
            email="existing@example.com"
        )
        user_service_mock.create.assert_not_called()

    async def test_update_current_user_success(
        self,
        user_service_mock,
        graphql_client,
        current_user_mock,
        db_session_mock,
    ):
        user_service_mock.get_one_or_none.return_value = None

        mutation = """
        mutation UpdateCurrentUser($userInput: UpdateUserInput!) {
            updateCurrentUser(userInput: $userInput) {
                id
                email
                firstName
                lastName
            }
        }
        """
        variables = {
            "userInput": {
                "email": "updated@example.com",
                "firstName": "Updated",
                "lastName": "User",
            }
        }
        result = await graphql_client.mutation(mutation, variables=variables)

        assert "errors" not in result
        assert "data" in result
        expected_user_data = {
            "id": to_base64("UserType", "1"),
            "firstName": "Updated",
            "lastName": "User",
            "email": "updated@example.com",
        }
        assert result["data"]["updateCurrentUser"] == expected_user_data

        user_service_mock.get_one_or_none.assert_called_once_with(
            email="updated@example.com"
        )
        db_session_mock.commit.assert_called_once()
        assert current_user_mock.email == "updated@example.com"
        assert current_user_mock.first_name == "Updated"
        assert current_user_mock.last_name == "User"

    async def test_update_current_user_email_taken(
        self,
        user_service_mock,
        graphql_client,
        current_user_mock,
    ):
        existing_user = UserModel(
            email="existing@example.com",
            password_hash="hashed",
            first_name="Existing",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        existing_user.id = 2
        user_service_mock.get_one_or_none.return_value = existing_user

        mutation = """
        mutation UpdateCurrentUser($userInput: UpdateUserInput!) {
            updateCurrentUser(userInput: $userInput) {
                id
                email
            }
        }
        """
        variables = {
            "userInput": {
                "email": "existing@example.com",
            }
        }
        result = await graphql_client.mutation(mutation, variables=variables)

        assert "errors" in result
        assert len(result["errors"]) == 1
        assert (
            "User with email 'existing@example.com' already exists"
            in result["errors"][0]["message"]
        )
        user_service_mock.get_one_or_none.assert_called_once_with(
            email="existing@example.com"
        )

    async def test_login_success(self, user_service_mock, graphql_client):
        from argon2 import PasswordHasher

        ph = PasswordHasher()
        password = "SecurePassword123!"
        hashed = ph.hash(password)

        mock_user = UserModel(
            email="login@example.com",
            password_hash=hashed,
            first_name="Login",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        mock_user.id = 1
        user_service_mock.get_one_or_none.return_value = mock_user

        mutation = """
        mutation Login($email: String!, $password: String!) {
            login(email: $email, password: $password) {
                token
                user {
                    id
                    email
                }
            }
        }
        """
        variables = {"email": "login@example.com", "password": password}
        result = await graphql_client.mutation(mutation, variables=variables)

        assert "data" in result
        assert "login" in result["data"]
        login_data = result["data"]["login"]
        assert login_data["token"] is not None
        assert len(login_data["token"]) > 0
        assert login_data["user"]["email"] == "login@example.com"

    async def test_login_reactivates_deleted_user(
        self, user_service_mock, graphql_client, db_session_mock
    ):
        import datetime

        from argon2 import PasswordHasher

        ph = PasswordHasher()
        password = "SecurePassword123!"
        hashed = ph.hash(password)

        mock_user = UserModel(
            email="reactivate@example.com",
            password_hash=hashed,
            first_name="Reactivate",
            last_name="User",
            is_admin=False,
            is_active=True,
            deleted_at=datetime.datetime.now(datetime.UTC),
        )
        mock_user.id = 1
        user_service_mock.get_one_or_none.return_value = mock_user

        mutation = """
        mutation Login($email: String!, $password: String!) {
            login(email: $email, password: $password) {
                token
                reactivated
                user {
                    id
                    email
                }
            }
        }
        """
        variables = {"email": "reactivate@example.com", "password": password}
        result = await graphql_client.mutation(mutation, variables=variables)

        assert "data" in result
        assert "login" in result["data"]
        login_data = result["data"]["login"]
        assert login_data["reactivated"] is True
        assert login_data["user"]["email"] == "reactivate@example.com"
        assert mock_user.deleted_at is None
        db_session_mock.commit.assert_called_once()

    async def test_login_invalid_credentials(self, user_service_mock, graphql_client):
        from argon2 import PasswordHasher

        ph = PasswordHasher()
        # Mock user exists but password will be wrong
        mock_user = UserModel(
            email="login@example.com",
            password_hash=ph.hash("CorrectPassword"),
            first_name="Login",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        mock_user.id = 1
        user_service_mock.get_one_or_none.return_value = mock_user

        mutation = """
        mutation Login($email: String!, $password: String!) {
            login(email: $email, password: $password) {
                token
            }
        }
        """
        variables = {"email": "login@example.com", "password": "WrongPassword"}
        result = await graphql_client.mutation(mutation, variables=variables)

        assert "errors" in result
        assert result["errors"][0]["message"] == "Invalid credentials"

    async def test_soft_delete_current_user(
        self, graphql_client, current_user_mock, db_session_mock
    ):
        mutation = """
        mutation SoftDeleteCurrentUser {
            softDeleteCurrentUser
        }
        """
        result = await graphql_client.mutation(mutation)

        assert "errors" not in result
        assert result["data"]["softDeleteCurrentUser"] is True
        current_user_mock.soft_delete.assert_called_once()
        db_session_mock.commit.assert_called_once()
