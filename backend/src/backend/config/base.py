from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
    postgres_test_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    # Used by test runner / Taskfile to force using postgres_test_db without
    # requiring different env var names.
    use_test_db: bool = False

    # SQLAdmin session auth
    # Used as Starlette SessionMiddleware secret_key (required to protect /admin).
    admin_session_secret: str | None = None


settings = Settings()  # type: ignore[call-arg]
