from functools import cached_property

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

    @cached_property
    def postgres_test_db(self) -> str:
        return f"{self.postgres_db}_test"


settings = Settings()  # type: ignore[call-arg]
