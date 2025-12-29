from celery import Celery
from celery.schedules import crontab

from backend.config.base import settings

# Set the default Django settings module for the 'celery' program.
# Not using Django, but standard pattern.
# For Litestar, we might not need this env var for the app itself, but good for context.

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
