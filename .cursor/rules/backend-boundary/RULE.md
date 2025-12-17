---
description: Backend rules for Litestar/Python; keep changes scoped, consistent, and contract-safe.
alwaysApply: true
---

## Scope boundary
- Keep backend changes inside `backend/`.
- Cross-repo edits are allowed **only when required by the task** or required to keep contracts/examples in sync:
  - GraphQL schema/codegen outputs (e.g., `task backend:schema:export` / `task frontend:codegen`)
  - `.env.example` / README updates when backend env vars or workflows change

## Conventions
- Follow existing Litestar conventions and project structure already in this repo.
- Avoid drive-by refactors; change only what the task requires.

## Dependencies
- Avoid introducing new dependencies unless clearly justified and confirmed.

## GraphQL / contract-sensitive changes
- If you change GraphQL behavior/schema: call it out, confirm if it impacts the contract, then run the repo’s codegen workflow (`task frontend:codegen`) so the frontend stays in sync.
