from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    admin_session_secret: str

    cors_allow_origins: list[str]
    jwt_secret: str
    rate_limit_per_minute_anonymous: int = 10
    rate_limit_per_minute_authenticated: int = 100

    celery_broker_url: str
    celery_result_backend: str
    celery_timezone: str = "UTC"
    celery_result_expires_seconds: int = 60 * 60  # 1 hour


settings = Settings()  # type: ignore[call-arg]
