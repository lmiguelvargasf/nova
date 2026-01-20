---
applyTo: "**/*.py"
---

# Python instructions

## Prime directive: no guessing

- If required context is missing (caller expectations, types, invariants, IO behavior),
  stop and ask for what’s missing rather than inventing it.
- Never invent modules, functions, env vars, CLI commands, or APIs that are not
  already present in the repo. If something is referenced but not found, say so.

## Minimal, scoped changes (correctness > churn)

- Change only what the task requires. No drive-by refactors.
- Do not rename identifiers, reorder code, or reformat unrelated sections.
- Prefer the smallest diff that preserves readability and keeps `ruff` + `ty` happy.

## Tooling is the source of truth (ruff + ty)

- Formatting: use ruff format (line length 88, target `py314`).
- Linting: fix issues rather than suppressing; use `# noqa: <CODES>` only when justified.
- Re-exports: use `from .module import X as X` instead of suppressing `F401` or
  adding `__all__` just to appease lint.
- Imports: prefer absolute imports from the package root; sibling imports (`.`)
  are acceptable.
- Exceptions (TRY003): avoid long formatted strings in `raise`; prefer a custom
  exception class.
- Typing: keep code ty-clean; avoid `Any`/`cast()` unless bridging an
  external/untyped boundary.

## Style & comments

- Follow PEP 8/PEP 257 as enforced by ruff.
- Keep formatting consistent with the existing file; don’t beautify unrelated code.
- Minimize comments; add them only when intent/invariants are not obvious.

## Repo constraints

- Python `>=3.14` (modern syntax only when needed).
- Dependencies managed with `uv`; do not add packages without explicit permission.
- Backend logic stays in `backend/`; do not import from `frontend/` into
  backend code.
- Backend stack: Litestar, Strawberry GraphQL, Advanced Alchemy/SQLAlchemy async,
  `pydantic-settings`.

## Modern typing

- Add accurate type hints for public functions/methods.
- Prefer `X | Y`, built-in generics, and `collections.abc` for interfaces.
- Model dynamic data explicitly (e.g., `TypedDict`, `Protocol`) instead of
  lying to the type checker.
- Avoid `from __future__ import annotations` unless already present or required.

## Async + resource safety

- Use `async def` for request/DB/IO code.
- Use context managers for sessions, files, locks, etc.
- Avoid blocking calls in async paths unless explicitly accepted by the task.

## Database rules

- Prefer existing session acquisition patterns (e.g., `alchemy_config.get_session()`
  or injected `AsyncSession`).
- Keep transactions explicit: use `flush()` for DB-generated values; `commit()`
  only when finalizing changes.
- Prefer SQLAlchemy expressions over raw SQL unless required.
- Any schema/model change should use the migration workflow.

## Configuration/settings (Pydantic v2)

- Don’t introduce new required env vars casually.
- If settings change, update `Settings` and keep docs/examples in sync
  (`README`, `.env.example`, `backend/.env.example`) as needed.

## Strawberry GraphQL rules

- Keep types/queries/mutations/inputs in existing modules under `backend/src/backend/apps/**/graphql/`.
- Resolvers should be thin; move workflows into `services.py`.
- For user-visible errors, raise `GraphQLError` with a safe message.
- Prefer typing the GraphQL context.
- Relay IDs:
  - GraphQL `ID` values are Relay Global IDs.
  - Use `strawberry.relay.Node` with `relay.NodeID[int]` for persisted entities.
  - Prefer `*_by_id(id: strawberry.relay.GlobalID)` or `Query.node(id: ID!)`
    for details.
  - Prefer Relay connections for lists and use `node.id` for list → details.

## REST pagination (Litestar)

- Prefer cursor/keyset pagination for list endpoints.
- Contract: request `limit` + optional `cursor`, response
  `{ items, page: { next_cursor, limit, has_next } }`.
- Reject malformed/tampered cursors and cursor reuse after filter/sort changes.

## Errors must not disappear

- Do not swallow exceptions; catch only what you can handle and re-raise otherwise.
- Narrow exception: auth/password verification may return a safe failure value,
  but keep scope minimal and justify broad catches.

## Logging vs print

- Do not add `print()` for non-trivial codepaths.
- Prefer existing logging conventions; if none exist, use `loguru` (no new deps).
- Never log secrets.

## Docstrings

- Add docstrings only for public APIs or non-obvious logic.
- Use `"""` docstrings that describe behavior, inputs/outputs, side effects,
  and exceptions.

## Tests & completion bar

- Update/add tests when behavior changes (pytest + pytest-asyncio).
- Type annotations are optional in `tests/` and scripts.
- Before declaring backend work done, prefer: `task backend:format`,
  `task backend:lint`, `task backend:typecheck`, `task backend:test`.
