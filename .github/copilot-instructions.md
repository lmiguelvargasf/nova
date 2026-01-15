# AI Coding Agent Instructions

## Project Overview

Nova is a full-stack template:

- Backend: Python 3.14 + Litestar + Postgres + Redis
- Frontend: TypeScript + Next.js 16 + React 19
- API: GraphQL + REST (either or both)
- Async: Celery workers + Beat

## Architecture Highlights

- Backend domains live in `backend/src/backend/apps/<domain>/`
- Frontend App Router in `frontend/src/app/`, features in
  `frontend/src/features/`
- GraphQL schema defined in `backend/src/backend/graphql/schema.py`
- Taskfile (`task` CLI) is the workflow source of truth

## Where rules live

- Always-on standards: `.github/instructions/*`
- Task-specific workflows: `.github/skills/*`

## Key files

- Backend app: `backend/src/backend/application.py`
- Settings: `backend/src/backend/config/base.py`
- GraphQL schema: `backend/src/backend/graphql/schema.py`
- Celery: `backend/src/backend/celery_app.py`
- Frontend home: `frontend/src/app/page.tsx`
- Next config: `frontend/next.config.ts`
- Taskfile: `Taskfile.yml`
- Docker: `compose.yaml`
