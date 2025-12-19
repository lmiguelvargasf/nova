from backend.apps.users.models import UserModel


def test_user_model_smoke() -> None:
    user = UserModel(
        email="test@example.com",
        password_hash="hashed",
        first_name="Test",
        last_name="User",
        is_admin=False,
        is_active=True,
    )
    user.id = 1

    assert user.id == 1
    assert user.email == "test@example.com"
