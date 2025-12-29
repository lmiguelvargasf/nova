from collections.abc import AsyncIterator

import pytest
from advanced_alchemy.extensions.litestar import SQLAlchemyAsyncConfig
from argon2 import PasswordHasher
from litestar import Litestar
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_409_CONFLICT,
)
from litestar.testing import AsyncTestClient
from sqlalchemy import select

from backend.application import create_app
from backend.apps import models as app_models
from backend.apps.users.models import UserModel
from backend.auth.jwt import jwt_auth
from backend.config.alchemy import build_connection_string, session_config
from backend.config.base import settings


async def _create_user(
    db_sessionmaker,
    *,
    email: str,
    password: str = "SecurePassword123!",
    first_name: str = "Test",
    last_name: str = "User",
    is_admin: bool = False,
    is_active: bool = True,
) -> UserModel:
    async with db_sessionmaker() as session:
        ph = PasswordHasher()
        user_model = UserModel(
            email=email,
            password_hash=ph.hash(password),
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin,
            is_active=is_active,
        )
        session.add(user_model)
        await session.commit()
        await session.refresh(user_model)
        return user_model


@pytest.fixture
async def user(db_sessionmaker) -> UserModel:
    return await _create_user(db_sessionmaker, email="user@example.com")


@pytest.fixture
async def other_user(db_sessionmaker) -> UserModel:
    return await _create_user(db_sessionmaker, email="other@example.com")


@pytest.fixture
async def rest_client(
    db_schema: None,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[AsyncTestClient[Litestar]]:
    async def retrieve_user_handler(token, _connection):
        try:
            user_id = int(token.sub)
        except (TypeError, ValueError):
            return None
        return UserModel(id=user_id)

    monkeypatch.setattr(jwt_auth, "retrieve_user_handler", retrieve_user_handler)
    config = SQLAlchemyAsyncConfig(
        connection_string=build_connection_string(db_name=settings.postgres_test_db),
        session_config=session_config,
        metadata=app_models.metadata,
        create_all=False,
    )
    test_app = create_app(
        use_sqlalchemy_plugin=True,
        enable_admin=False,
        alchemy_config_override=config,
    )
    async with AsyncTestClient(app=test_app) as client:
        yield client


async def test_rest_soft_delete_reactivates_user(
    rest_client: AsyncTestClient[Litestar],
    db_sessionmaker,
) -> None:
    payload = {
        "email": "rest@example.com",
        "password": "SecurePassword123!",
        "first_name": "Rest",
        "last_name": "User",
    }
    register_response = await rest_client.post(
        "/api/auth/register",
        json=payload,
    )
    assert register_response.status_code == HTTP_201_CREATED
    register_data = register_response.json()
    token = register_data["token"]
    assert register_data["reactivated"] is False
    assert register_data["user"]["email"] == payload["email"]

    headers = {"Authorization": f"Bearer {token}"}
    me_response = await rest_client.get("/api/users/me", headers=headers)
    assert me_response.status_code == HTTP_200_OK
    assert me_response.json()["email"] == payload["email"]

    delete_response = await rest_client.delete("/api/users/me", headers=headers)
    assert delete_response.status_code == HTTP_200_OK
    assert delete_response.json() == {"deleted": True}

    async with db_sessionmaker() as session:
        user = await session.scalar(
            select(UserModel).where(UserModel.email == payload["email"])
        )
        assert user is not None
        assert user.deleted_at is not None

    login_response = await rest_client.post(
        "/api/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login_response.status_code == HTTP_201_CREATED
    login_data = login_response.json()
    assert login_data["reactivated"] is True
    assert login_data["token"]

    async with db_sessionmaker() as session:
        user = await session.scalar(
            select(UserModel).where(UserModel.email == payload["email"])
        )
        assert user is not None
        assert user.deleted_at is None


async def test_rest_me_unauthenticated(rest_client: AsyncTestClient[Litestar]) -> None:
    response = await rest_client.get("/api/users/me")
    assert response.status_code == HTTP_401_UNAUTHORIZED


async def test_rest_list_users_unauthenticated(
    rest_client: AsyncTestClient[Litestar],
) -> None:
    response = await rest_client.get("/api/users")
    assert response.status_code == HTTP_401_UNAUTHORIZED


async def test_rest_list_users_non_admin(
    rest_client: AsyncTestClient[Litestar],
    user: UserModel,
) -> None:
    token = jwt_auth.create_token(identifier=str(user.id))
    response = await rest_client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTP_403_FORBIDDEN


async def test_rest_list_users_cursor_pagination(
    rest_client: AsyncTestClient[Litestar],
    db_sessionmaker,
) -> None:
    admin = await _create_user(
        db_sessionmaker, email="admin@example.com", is_admin=True
    )
    token = jwt_auth.create_token(identifier=str(admin.id))

    for i in range(12):
        await _create_user(db_sessionmaker, email=f"user-{i}@example.com")

    response1 = await rest_client.get(
        "/api/users?limit=5",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response1.status_code == HTTP_200_OK
    data1 = response1.json()
    assert len(data1["items"]) == 5
    assert data1["page"]["limit"] == 5
    assert data1["page"]["has_next"] is True
    assert data1["page"]["next_cursor"]

    cursor = data1["page"]["next_cursor"]
    emails1 = {u["email"] for u in data1["items"]}

    response2 = await rest_client.get(
        f"/api/users?limit=5&cursor={cursor}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response2.status_code == HTTP_200_OK
    data2 = response2.json()
    assert len(data2["items"]) == 5
    assert data2["page"]["has_next"] is True
    assert data2["page"]["next_cursor"]
    emails2 = {u["email"] for u in data2["items"]}
    assert emails1.isdisjoint(emails2)

    cursor2 = data2["page"]["next_cursor"]
    response3 = await rest_client.get(
        f"/api/users?limit=5&cursor={cursor2}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response3.status_code == HTTP_200_OK
    data3 = response3.json()
    assert len(data3["items"]) == 3
    assert data3["page"]["has_next"] is False
    assert data3["page"]["next_cursor"] is None


async def test_rest_list_users_invalid_cursor(
    rest_client: AsyncTestClient[Litestar],
    db_sessionmaker,
) -> None:
    admin = await _create_user(
        db_sessionmaker, email="admin2@example.com", is_admin=True
    )
    token = jwt_auth.create_token(identifier=str(admin.id))

    response = await rest_client.get(
        "/api/users?limit=5&cursor=not-a-cursor",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTP_400_BAD_REQUEST


async def test_rest_list_users_cursor_filter_mismatch(
    rest_client: AsyncTestClient[Litestar],
    db_sessionmaker,
) -> None:
    admin = await _create_user(
        db_sessionmaker, email="admin4@example.com", is_admin=True
    )
    token = jwt_auth.create_token(identifier=str(admin.id))

    for i in range(3):
        await _create_user(db_sessionmaker, email=f"filter-{i}@example.com")

    response1 = await rest_client.get(
        "/api/users?limit=2&searchString=filter",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response1.status_code == HTTP_200_OK
    cursor = response1.json()["page"]["next_cursor"]
    assert cursor

    # Change filters while reusing cursor should be rejected
    response2 = await rest_client.get(
        f"/api/users?limit=2&cursor={cursor}&searchString=other",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response2.status_code == HTTP_400_BAD_REQUEST


async def test_rest_list_users_limit_too_large(
    rest_client: AsyncTestClient[Litestar],
    db_sessionmaker,
) -> None:
    admin = await _create_user(
        db_sessionmaker, email="admin3@example.com", is_admin=True
    )
    token = jwt_auth.create_token(identifier=str(admin.id))

    response = await rest_client.get(
        "/api/users?limit=101",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTP_400_BAD_REQUEST


async def test_rest_update_me_invalid_input(
    rest_client: AsyncTestClient[Litestar],
    user: UserModel,
) -> None:
    token = jwt_auth.create_token(identifier=str(user.id))
    response = await rest_client.patch(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "   "},
    )
    assert response.status_code == HTTP_400_BAD_REQUEST


async def test_rest_update_me_duplicate_email(
    rest_client: AsyncTestClient[Litestar],
    user: UserModel,
    other_user: UserModel,
) -> None:
    token = jwt_auth.create_token(identifier=str(user.id))
    response = await rest_client.patch(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": other_user.email},
    )
    assert response.status_code == HTTP_409_CONFLICT


async def test_rest_register_duplicate_email(
    rest_client: AsyncTestClient[Litestar],
    user: UserModel,
) -> None:
    response = await rest_client.post(
        "/api/auth/register",
        json={
            "email": user.email,
            "password": "AnotherPassword123!",
            "first_name": "Dup",
            "last_name": "User",
        },
    )
    assert response.status_code == HTTP_409_CONFLICT


async def test_rest_update_me_password_success(
    rest_client: AsyncTestClient[Litestar],
    user: UserModel,
    db_sessionmaker,
) -> None:
    old_hash = user.password_hash
    new_password = "NewPassword123!"
    token = jwt_auth.create_token(identifier=str(user.id))
    response = await rest_client.patch(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"password": new_password},
    )
    assert response.status_code == HTTP_200_OK

    async with db_sessionmaker() as session:
        updated_user = await session.get(UserModel, user.id)

    assert updated_user is not None
    assert updated_user.password_hash != old_hash
    ph = PasswordHasher()
    assert ph.verify(updated_user.password_hash, new_password)


async def test_rest_login_invalid_credentials(
    rest_client: AsyncTestClient[Litestar],
    user: UserModel,
) -> None:
    response = await rest_client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "WrongPassword123!"},
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED


async def test_rest_login_inactive_user(
    rest_client: AsyncTestClient[Litestar],
    db_sessionmaker,
) -> None:
    user = await _create_user(
        db_sessionmaker,
        email="inactive@example.com",
        password="InactivePassword123!",
        is_active=False,
    )
    response = await rest_client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "InactivePassword123!"},
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
