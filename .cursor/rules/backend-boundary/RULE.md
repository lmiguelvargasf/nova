---
description: Backend boundary rules (Litestar, Advanced Alchemy/SQLAlchemy, Strawberry, Python 3.14+); keep changes scoped, consistent, and contract-safe.
globs:
  - "backend/**/*"
  - "Taskfile.yml"
  - "compose.yaml"
  - "frontend/schema/schema.graphql"
alwaysApply: false
---

## 1) Scope Boundary
- **Isolation**: Keep all backend logic within `backend/`. Never import from `frontend/`.
- **Cross-repo changes**: Allowed **only when required by the task** or required to keep contracts/examples in sync:
  - GraphQL schema/codegen outputs (e.g., `task backend:schema:export` / `task frontend:codegen`)
  - `.env.example` / README updates when backend env vars or workflows change

## 2) Technology Stack & Standards
- **Framework**: Litestar (`litestar[standard]`). Prefer `async def` handlers for request/IO code.
- **ORM**: SQLAlchemy via **Advanced Alchemy** (async, Postgres via `asyncpg`).
- **GraphQL**: Strawberry + `strawberry.litestar` integration.
- **Python**: `>=3.14` (use modern typing; keep type hints accurate for `pyrefly`).
- **Settings/Validation**: `pydantic-settings` (Pydantic v2) for configuration; use Pydantic models when validation is non-trivial.
- **Package manager**: `uv` (`uv.lock` exists).
- **Dependencies**: Managed with `uv`. Do not add packages without explicit permission.

## 3) Conventions
- Follow existing Litestar conventions and project structure already in this repo.
- Avoid drive-by refactors; change only what the task requires.

## 4) Code Organization
- Keep Strawberry **types/queries/mutations/inputs** in their respective module files under `backend/src/backend/apps/**/graphql/` (mirror the existing layout).
- Keep resolvers/handlers **small and readable**. If logic grows (multi-step workflows, complex validation, cross-table operations), move it into a local service module (within `backend/`) and call it from the resolver/handler.

## 5) Database & Migrations
- Do **not** manually change DB schema/state outside the repo migration workflow (`litestar database ...`).
- Any SQLAlchemy model/table change should come with an appropriate migration and a clear note about how to apply it.
- Prefer Taskfile workflows. If a required workflow is missing (e.g., “create a migration”), add a Task target rather than documenting multi-step manual commands as the official process.

## 6) GraphQL & Contracts
- If you change GraphQL behavior/schema: call it out, confirm if it impacts the contract, then run the repo’s codegen workflow (`task frontend:codegen`) so the frontend stays in sync.

## 7) Validation Workflow
Before declaring a backend task complete:
- **Run**:
  - `task backend:format`
  - `task backend:lint:fix`
  - `task backend:typecheck`
  - `task backend:test`
- **If GraphQL was touched**: run `task frontend:codegen` and ensure `frontend/schema/schema.graphql` updates accordingly.
