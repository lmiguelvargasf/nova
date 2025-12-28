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


async def create_user(
    db_sessionmaker,
    *,
    email: str,
    password: str = "SecurePassword123!",
    first_name: str = "Test",
    last_name: str = "User",
    is_admin: bool = False,
) -> UserModel:
    async with db_sessionmaker() as session:
        ph = PasswordHasher()
        user = UserModel(
            email=email,
            password_hash=ph.hash(password),
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


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
    db_sessionmaker,
) -> None:
    user = await create_user(db_sessionmaker, email="nonadmin@example.com")
    token = jwt_auth.create_token(identifier=str(user.id))
    response = await rest_client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTP_403_FORBIDDEN


async def test_rest_update_me_invalid_input(
    rest_client: AsyncTestClient[Litestar],
    db_sessionmaker,
) -> None:
    user = await create_user(db_sessionmaker, email="invalid@example.com")
    token = jwt_auth.create_token(identifier=str(user.id))
    response = await rest_client.patch(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "   "},
    )
    assert response.status_code == HTTP_400_BAD_REQUEST


async def test_rest_update_me_duplicate_email(
    rest_client: AsyncTestClient[Litestar],
    db_sessionmaker,
) -> None:
    user = await create_user(db_sessionmaker, email="owner@example.com")
    other_user = await create_user(db_sessionmaker, email="taken@example.com")
    token = jwt_auth.create_token(identifier=str(user.id))
    response = await rest_client.patch(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": other_user.email},
    )
    assert response.status_code == HTTP_409_CONFLICT
