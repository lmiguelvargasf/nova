from advanced_alchemy.extensions.litestar import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)

from backend.apps.users.models import UserModel

from .base import settings


def build_connection_string(*, use_test_db: bool | None = None) -> str:
    """
    Build the SQLAlchemy async Postgres connection string from existing settings.

    We intentionally avoid introducing new required env vars (e.g. DATABASE_URL).
    """

    if use_test_db is None:
        use_test_db = settings.use_test_db

    db_name = settings.postgres_test_db if use_test_db else settings.postgres_db
    return (
        "postgresql+asyncpg://"
        f"{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/{db_name}"
    )


session_config = AsyncSessionConfig(expire_on_commit=False)

alchemy_config = SQLAlchemyAsyncConfig(
    connection_string=build_connection_string(),
    before_send_handler="autocommit",
    session_config=session_config,
    # Ensure the migration/autogenerate machinery sees all imported models.
    metadata=UserModel.metadata,
    # We use Alembic migrations for schema management.
    create_all=False,
)
