---
name: guardrails
description: Use for change discipline, validation expectations, and safety checks when making repo changes.
---

# Guardrails

## When to use
- You are planning changes that might touch multiple areas or risk unintended churn.
- You are preparing to declare work complete and need validation guidance.

## Steps
1. Keep changes small and incremental; avoid drive-by refactors.
2. Touch the fewest files necessary; avoid cross-module churn.
3. Follow existing patterns and conventions; do not invent new architecture.
4. If behavior changes, add/update tests to cover it.
5. Use Taskfile targets for validation:
   - Backend: `task backend:format`, `task backend:lint`, `task backend:typecheck`, `task backend:test`.
   - Frontend: `task frontend:format`, `task frontend:lint`, `task frontend:check`, `task frontend:test:run`.
   - GraphQL touched: `task frontend:codegen`.
6. If a check can’t run, state what ran and what was blocked.

## Constraints and guardrails
- Never commit secrets or real credentials (use `.env.example`).
- Avoid cross-cutting backend + frontend changes unless explicitly required.
- Ask/confirm before changes to:
  - API/GraphQL schema/contract, auth/session/security logic, or data model/migrations
  - Dependencies or lockfile changes not required by the task

## References
- `.env.example`
- `Taskfile.yml`
- `backend/Taskfile.yml`
- `frontend/Taskfile.yml`
