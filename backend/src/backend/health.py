from litestar import get
from msgspec import Struct


class HealthStatus(Struct):
    status: str


@get("/health")
async def health_check() -> HealthStatus:
    return HealthStatus(status="ok")
