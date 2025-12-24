---
description: Repo-wide guardrails for safe, consistent changes
alwaysApply: true
---

## Change discipline
- Prefer **small, incremental changes** over large or sweeping edits.
- Avoid **drive-by refactors** (renames/reformatting/restructure) unless required for the task.
- Keep diffs **local**: touch the smallest number of files needed; avoid cross-module churn.
- Don’t invent architecture; follow existing patterns and conventions in the repo.

## Validation before completion
- Prefer running checks via **Taskfile** (repo default).
  - Backend (if backend code touched): `task backend:format`, `task backend:lint`, `task backend:typecheck`, `task backend:test`
  - Frontend (if frontend code touched): `task frontend:format`, `task frontend:lint`, `task frontend:check`, `task frontend:test:run`
  - GraphQL schema/ops touched: `task frontend:codegen` (includes schema export)
- If changing behavior, add/update tests to cover the new behavior and regressions.
- If a check can’t be run (e.g., Docker not available), state **what you ran**, what was blocked, and why.

## Safety & scope
- Never commit secrets or real credentials (including in `.env*`); use `.env.example`.
- Avoid cross-cutting backend + frontend changes unless explicitly required.
- Ask/confirm before changes to:
  - API/GraphQL schema or contract, auth/session/security logic, or data model/migrations
  - Dependencies (new packages) or lockfile churn not required by the task

## When uncertain
- Inspect nearby code and mirror existing patterns.
- If the task is non-trivial (multi-file behavior changes, contract changes, data model changes), propose a short step plan and confirm assumptions before implementing.
