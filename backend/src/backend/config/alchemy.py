from advanced_alchemy.extensions.litestar import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)

from backend.apps import models as app_models

from .base import settings


def build_connection_string(db_name: str | None = None) -> str:
    """
    Build the SQLAlchemy async Postgres connection string from existing settings.

    We intentionally avoid introducing new required env vars (e.g. DATABASE_URL).
    """

    target_db = db_name or settings.postgres_db
    return (
        "postgresql+asyncpg://"
        f"{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/{target_db}"
    )


session_config = AsyncSessionConfig(expire_on_commit=False)

alchemy_config = SQLAlchemyAsyncConfig(
    connection_string=build_connection_string(),
    before_send_handler="autocommit",
    session_config=session_config,
    # Ensure the migration/autogenerate machinery sees all imported models.
    metadata=app_models.metadata,
    # We use Alembic migrations for schema management.
    create_all=False,
)
