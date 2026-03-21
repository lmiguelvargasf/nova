from collections.abc import AsyncIterator

import pytest
from argon2 import PasswordHasher
from litestar import Litestar
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from starlette_admin.contrib.sqla import ModelView

from backend.application import create_app
from backend.apps.users.models import UserModel
from backend.apps.users.services import UserService
from backend.graphql.context import GraphQLContext, Services


def _create_graphql_context_getter(mocker):
    async def context_getter() -> GraphQLContext:
        db_session_mock = mocker.Mock(spec=AsyncSession)
        user_service_mock = mocker.Mock(spec=UserService)

        services = Services(db_session_mock)
        services.users = user_service_mock

        return GraphQLContext(
            db_session=db_session_mock,
            services=services,
        )

    return context_getter


@pytest.fixture
async def admin_test_client(
    db_engine, mocker
) -> AsyncIterator[AsyncTestClient[Litestar]]:
    admin_engine = create_async_engine(
        db_engine.url,
        poolclass=NullPool,
    )
    test_app = create_app(
        graphql_context_getter=_create_graphql_context_getter(mocker),
        use_sqlalchemy_plugin=False,
        enable_admin=True,
        admin_engine=admin_engine,
    )
    async with AsyncTestClient(app=test_app) as client:
        yield client
    await admin_engine.dispose()


async def test_admin_redirects_to_login_when_unauthenticated(
    admin_test_client: AsyncTestClient[Litestar],
) -> None:
    response = await admin_test_client.get("/admin", follow_redirects=False)
    assert response.status_code == 303
    assert "/admin/login" in response.headers["location"]


async def test_admin_route_identity_starting_with_admin_redirects_to_login(
    db_engine,
    mocker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import backend.admin.app as admin_app_module

    admin_users_view = ModelView(
        UserModel,
        identity="admin-users",
        name="Admin User",
        label="Admin Users",
    )
    monkeypatch.setattr(
        admin_app_module,
        "ADMIN_VIEWS",
        [*admin_app_module.ADMIN_VIEWS, admin_users_view],
    )

    admin_engine = create_async_engine(
        db_engine.url,
        poolclass=NullPool,
    )
    test_app = create_app(
        graphql_context_getter=_create_graphql_context_getter(mocker),
        use_sqlalchemy_plugin=False,
        enable_admin=True,
        admin_engine=admin_engine,
    )
    try:
        async with AsyncTestClient(app=test_app) as client:
            response = await client.get(
                "/admin/admin-users/list",
                follow_redirects=False,
            )
    finally:
        await admin_engine.dispose()

    assert response.status_code == 303
    assert "/admin/login" in response.headers["location"]


async def test_admin_login_success(
    admin_test_client: AsyncTestClient[Litestar],
    db_sessionmaker,
) -> None:
    ph = PasswordHasher()
    async with db_sessionmaker() as session:
        session.add(
            UserModel(
                email="admin@example.com",
                password_hash=ph.hash("TestPassword123"),
                first_name="Admin",
                last_name="User",
                is_admin=True,
                is_active=True,
            )
        )
        await session.commit()

    response = await admin_test_client.post(
        "/admin/login",
        data={"username": "admin@example.com", "password": "TestPassword123"},
        follow_redirects=False,
    )
    assert response.status_code == 303

    response = await admin_test_client.get("/admin")
    assert response.status_code == 200
