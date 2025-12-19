from backend.apps.users.models import UserModel
from backend.security.passwords import hash_password


async def test_user_model_create_and_get(db_sessionmaker) -> None:
    async with db_sessionmaker() as session:
        user = UserModel(
            email="test@example.com",
            password_hash=hash_password("TestPassword123"),
            first_name="Test",
            last_name="User",
            is_admin=False,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        user_id = user.id

    async with db_sessionmaker() as session:
        fetched = await session.get(UserModel, user_id)

    assert fetched is not None
    assert fetched.id == user_id
    assert fetched.email == "test@example.com"
