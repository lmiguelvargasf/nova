from unittest.mock import ANY

from strawberry.relay.utils import to_base64

from backend.apps.users.models import UserModel
from backend.apps.users.services import (
    InvalidCredentialsError as InvalidCredentialsServiceError,
)
from backend.apps.users.services import (
    UserAlreadyExistsError as UserAlreadyExistsServiceError,
)


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
        user_service_mock.create_user_account.return_value = mock_user

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

        user_service_mock.create_user_account.assert_called_once_with(
            db_session=ANY,
            email="new@example.com",
            password="TestPassword123",
            first_name="New",
            last_name="User",
            is_admin=False,
            is_active=True,
        )

    async def test_create_user_already_exists(self, user_service_mock, graphql_client):
        user_service_mock.create_user_account.side_effect = (
            UserAlreadyExistsServiceError("existing@example.com")
        )

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

        user_service_mock.create_user_account.assert_called_once_with(
            db_session=ANY,
            email="existing@example.com",
            password="TestPassword123",
            first_name="Test",
            last_name="User",
            is_admin=False,
            is_active=True,
        )

    async def test_update_current_user_success(
        self,
        user_service_mock,
        graphql_client,
        current_user_mock,
        db_session_mock,
    ):
        updated_user = UserModel(
            email="updated@example.com",
            password_hash="hashed",
            first_name="Updated",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        updated_user.id = 1
        user_service_mock.apply_user_updates.return_value = updated_user

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

        user_service_mock.apply_user_updates.assert_called_once_with(
            db_session=db_session_mock,
            user=current_user_mock,
            email="updated@example.com",
            first_name="Updated",
            last_name="User",
            password=None,
        )

    async def test_update_current_user_email_taken(
        self,
        user_service_mock,
        graphql_client,
    ):
        user_service_mock.apply_user_updates.side_effect = (
            UserAlreadyExistsServiceError("existing@example.com")
        )

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

    async def test_login_success(self, user_service_mock, graphql_client):
        password = "SecurePassword123!"
        mock_user = UserModel(
            email="login@example.com",
            password_hash="hashed",
            first_name="Login",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        mock_user.id = 1
        user_service_mock.authenticate_for_login.return_value = (mock_user, False)

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
        user_service_mock.authenticate_for_login.assert_called_once_with(
            db_session=ANY,
            email="login@example.com",
            password=password,
        )

    async def test_login_reactivates_deleted_user(
        self,
        user_service_mock,
        graphql_client,
    ):
        password = "SecurePassword123!"
        mock_user = UserModel(
            email="reactivate@example.com",
            password_hash="hashed",
            first_name="Reactivate",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        mock_user.id = 1
        user_service_mock.authenticate_for_login.return_value = (mock_user, True)

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
        user_service_mock.authenticate_for_login.assert_called_once_with(
            db_session=ANY,
            email="reactivate@example.com",
            password=password,
        )

    async def test_login_invalid_credentials(self, user_service_mock, graphql_client):
        user_service_mock.authenticate_for_login.side_effect = (
            InvalidCredentialsServiceError()
        )

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
        user_service_mock.authenticate_for_login.assert_called_once_with(
            db_session=ANY,
            email="login@example.com",
            password="WrongPassword",
        )

    async def test_soft_delete_current_user(
        self,
        graphql_client,
        current_user_mock,
        db_session_mock,
        user_service_mock,
    ):
        mutation = """
        mutation SoftDeleteCurrentUser {
            softDeleteCurrentUser
        }
        """
        result = await graphql_client.mutation(mutation)

        assert "errors" not in result
        assert result["data"]["softDeleteCurrentUser"] is True
        user_service_mock.soft_delete_user.assert_called_once_with(
            db_session=db_session_mock,
            user=current_user_mock,
        )
