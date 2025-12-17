---
description: Backend boundary rules (Litestar, Piccolo, Strawberry, Python 3.13+); keep changes scoped, consistent, and contract-safe.
alwaysApply: true
---

## Scope boundary
- Keep backend changes inside `backend/`.
- Cross-repo edits are allowed **only when required by the task** or required to keep contracts/examples in sync:
  - GraphQL schema/codegen outputs (e.g., `task backend:schema:export` / `task frontend:codegen`)
  - `.env.example` / README updates when backend env vars or workflows change

## Technology stack & standards (this repo)
- **Framework**: Litestar (`litestar[standard]`). Prefer `async def` handlers for request/IO code.
- **ORM**: Piccolo (Postgres). Follow Piccolo table patterns and query APIs.
- **GraphQL**: Strawberry + `strawberry.litestar` integration.
- **Python**: `>=3.13` (use modern typing; keep type hints accurate for `pyrefly`).
- **Settings/validation**: `pydantic-settings` (Pydantic v2) for configuration; use Pydantic models when validation is non-trivial.
- **Dependencies**: Managed with `uv` (`uv.lock` exists). Do not add packages without explicit permission.

## Conventions
- Follow existing Litestar conventions and project structure already in this repo.
- Avoid drive-by refactors; change only what the task requires.

## Code organization
- Keep Strawberry **types/queries/mutations/inputs** in their respective module files under `backend/src/backend/apps/**/graphql/` (mirror the existing layout).
- Keep resolvers/handlers **small and readable**. If logic grows (multi-step workflows, complex validation, cross-table operations), move it into a local service module (within `backend/`) and call it from the resolver/handler.

## Database & migrations
- Do **not** manually change DB schema/state outside Piccolo’s migration system.
- Any Piccolo table change should come with an appropriate migration and a clear note about how to apply it.
- Prefer Taskfile workflows. If a required workflow is missing (e.g., “create a migration”), add a Task target rather than documenting multi-step manual commands as the official process.

## GraphQL / contract-sensitive changes
- If you change GraphQL behavior/schema: call it out, confirm if it impacts the contract, then run the repo’s codegen workflow (`task frontend:codegen`) so the frontend stays in sync.

## Validation before completion (backend changes)
- Run:
  - `task backend:format`
  - `task backend:lint:fix`
  - `task backend:typecheck`
  - `task backend:test`
- If GraphQL schema/contract changed: run `task frontend:codegen` and ensure `frontend/schema/schema.graphql` updates accordingly.
