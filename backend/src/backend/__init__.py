from litestar import Litestar, asgi, get
from litestar.types import Receive, Scope, Send
from piccolo.apps.user.tables import BaseUser
from piccolo_admin.endpoints import create_admin
from pydantic import BaseModel
from strawberry.litestar import make_graphql_controller

from .db import close_database_connection_pool, open_database_connection_pool
from .schema import schema


@asgi("/admin/", is_mount=True, copy_scope=False)
async def admin(scope: Scope, receive: Receive, send: Send) -> None:
    await create_admin(tables=[BaseUser])(scope, receive, send)  # type: ignore[arg-type]


class HealthStatus(BaseModel):
    status: str


@get("/health")
async def health_check() -> HealthStatus:
    return HealthStatus(status="ok")


GraphQLController = make_graphql_controller(schema=schema, path="/graphql")

app = Litestar(
    route_handlers=[admin, health_check, GraphQLController],
    on_startup=[open_database_connection_pool],
    on_shutdown=[close_database_connection_pool],
)
