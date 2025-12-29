from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from celery import Celery, signals
from celery.schedules import crontab
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from backend.config.alchemy import build_connection_string
from backend.config.base import settings

app = Celery("backend")

app.conf.update(
    broker_url=settings.celery_broker_url,
    result_backend=settings.celery_result_backend,
    timezone=settings.celery_timezone,
    enable_utc=True,
)

app.conf.beat_schedule = {
    "deactivate-inactive-users-daily": {
        "task": "backend.apps.users.tasks.deactivate_inactive_users",
        "schedule": crontab(hour=3, minute=15),
    },
}

app.autodiscover_tasks(["backend.apps.users"])

# Global engine for worker process
_engine: AsyncEngine | None = None


@signals.worker_process_init.connect
def init_worker_engine(**kwargs: object) -> None:
    """
    Initialize a global AsyncEngine for the worker process.
    This runs once when a worker child process starts.
    """
    global _engine
    _engine = create_async_engine(build_connection_string())


@signals.worker_process_shutdown.connect
def shutdown_worker_engine(**kwargs: object) -> None:
    """
    Dispose of the global AsyncEngine when the worker process shuts down.
    """
    global _engine
    if _engine:
        # We can't await here because this signal might run in a sync context,
        # but for cleanup on shutdown, we can rely on process termination.
        pass


@asynccontextmanager
async def get_task_session() -> AsyncIterator[AsyncSession]:
    """
    Async context manager to provide a session for Celery tasks.
    Uses the worker-global engine if available, otherwise creates a temporary one
    (useful for testing or if signal handlers didn't run).
    """
    global _engine
    local_engine = False

    engine = _engine
    if engine is None:
        # Fallback if not initialized (e.g., testing or non-worker context)
        engine = create_async_engine(build_connection_string())
        local_engine = True

    try:
        async with AsyncSession(engine) as session, session.begin():
            yield session
    finally:
        if local_engine:
            await engine.dispose()
