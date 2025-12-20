from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
    postgres_test_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int


settings = Settings()  # type: ignore[call-arg]
