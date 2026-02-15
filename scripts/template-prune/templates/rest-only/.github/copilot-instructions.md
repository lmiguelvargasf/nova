# AI Coding Agent Instructions

## Project Overview

Nova is a backend REST template:

- Backend: Python 3.14 + Litestar + Postgres
- API: REST
- No GraphQL, frontend, iOS, or Celery stack in this profile

## Architecture Highlights

- Backend domains live in `backend/src/backend/apps/<domain>/`
- Taskfile (`task` CLI) is the workflow source of truth

## Where rules live

- Always-on standards: `.github/instructions/*`
- Task-specific workflows: `.github/skills/*`
- Task prompts: `.github/prompts/*` (lightweight workflow entry points;
  avoid duplicating rules)

## Prompt files

- `backend-entity`: backend entity scaffolding with REST + admin view.
- `taskfile-workflow`: add or update Taskfile targets.

## Key files

- Backend app: `backend/src/backend/application.py`
- Settings: `backend/src/backend/config/base.py`
- Taskfile: `Taskfile.yml`
- Docker: `compose.yaml`
