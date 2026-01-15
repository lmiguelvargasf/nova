---
name: backend-async-tasks
description: Use when creating or updating Celery tasks, async job logic, or Beat schedules in the backend.
---

# Backend async tasks (Celery)

## When to use
- You are adding or changing a Celery task in `backend/src/backend/apps/**/tasks.py`.
- You need to update the Celery Beat schedule in `backend/src/backend/celery_app.py`.
- You are adding DB access inside a Celery worker process.

## Steps
1. Define tasks only in a `tasks.py` file under the relevant app module.
2. Decorate tasks with `@app.task` imported from `backend.celery_app`.
3. Return a typed result (`int`, `None`, etc.). Keep task-specific parameters local unless they must be environment-configured.
4. For DB access:
   - Use `asyncio.run()` to bridge async work.
   - Always acquire a session via `get_task_session()` from `backend.celery_app`.
5. For periodic jobs, update `app.conf.beat_schedule` in `backend/src/backend/celery_app.py` and use `celery.schedules.crontab`.

## Constraints and guardrails
- Never use the global `alchemy_config` engine inside a task; it is not fork-safe for Celery workers.
- Always use `get_task_session()` to manage DB connections safely across worker processes.

## References
- `backend/src/backend/apps/**/tasks.py`
- `backend/src/backend/celery_app.py`
- `backend/tests/apps/users/test_tasks.py`
