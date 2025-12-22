from typing import Literal

from litestar import get
from msgspec import Struct


class HealthStatus(Struct):
    status: Literal["ok"]


@get("/health", tags=["System"], summary="Health check")
async def health_check() -> HealthStatus:
    return HealthStatus(status="ok")
