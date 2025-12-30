---
description: Standards for creating and managing background tasks and Celery workers
globs: ["backend/src/backend/apps/**/tasks.py", "backend/src/backend/celery_app.py"]
---

# Background Tasks

This project uses **Celery** for handling asynchronous background jobs and **Celery Beat** for periodic tasks, with **Redis** as the message broker.

## 1. Defining Tasks

-   Tasks MUST be defined in a `tasks.py` file within the relevant application module (e.g., `backend/src/backend/apps/users/tasks.py`).
-   Decorate tasks with `@app.task` imported from `backend.celery_app`.
-   Tasks MUST return a typed result (e.g., `int`, `None`).
-   Task-specific business parameters (like “inactive cutoff days”) SHOULD be kept local to the task unless you explicitly need environment-level tuning.

### Example

```python
from backend.celery_app import app

@app.task
def send_welcome_email(user_id: int) -> None:
    # Logic to send email
    pass
```

## 2. Database Access

-   Tasks are async-compatible via `asyncio.run()`.
-   **CRITICAL**: NEVER use the global `alchemy_config` engine directly inside a task, as it is not fork-safe for Celery workers.
-   **ALWAYS** use the `get_task_session()` helper from `backend.celery_app` to obtain a database session. It manages connection pooling safely across worker processes.

### Example with Database

```python
import asyncio
from backend.celery_app import app, get_task_session

@app.task
def prune_logs(days: int) -> int:
    return asyncio.run(_prune_logs_async(days))

async def _prune_logs_async(days: int) -> int:
    async with get_task_session() as session:
        # Perform DB operations
        return 0
```

## 3. Scheduling (Beat)

-   Periodic tasks (cron jobs) are defined in `app.conf.beat_schedule` within `backend/src/backend/celery_app.py`.
-   Use `celery.schedules.crontab` for timing.

```python
app.conf.beat_schedule = {
    "task-name": {
        "task": "backend.apps.users.tasks.deactivate_inactive_users",
        "schedule": crontab(hour=3, minute=15),
    },
}
```

## 4. Testing

-   When testing tasks, prefer dependency injection of a real `AsyncSession` to keep the test DB transaction deterministic.
-   See `backend/tests/apps/users/test_tasks.py` for examples.
