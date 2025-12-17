from piccolo.engine.postgres import PostgresEngine

from .base import settings

DB = PostgresEngine(
    config={
        "database": settings.postgres_test_db,
        "user": settings.postgres_user,
        "password": settings.postgres_password,
        "host": settings.postgres_host,
        "port": settings.postgres_port,
    }
)
