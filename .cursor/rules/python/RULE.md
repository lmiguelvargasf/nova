---
description: Python 3.14+ engineering rules (repo-aligned): correctness-first, no guessing, minimal diffs, ruff-formatted, pyrefly-clean.
globs:
  - "**/*.py"
alwaysApply: true
---

## 0) Prime Directive: No Guessing
- **In the face of ambiguity, refuse the temptation to guess.**
- If required context is missing (caller expectations, types, invariants, IO behavior), **stop** and ask for what’s missing rather than inventing it.
- Never invent modules, functions, env vars, CLI commands, or APIs that are not already present in the repo. If something is referenced but not found, say so.

## 1) Minimal, Scoped Changes (Correctness > Churn)
- Change only what the task requires. No drive-by refactors.
- Do not rename identifiers, reorder code, or reformat unrelated sections.
- Prefer the smallest diff that preserves readability and keeps `ruff` + `pyrefly` happy.

## 2) Tooling Is the Source of Truth (ruff + pyrefly)
- **Formatting**: this repo uses **ruff format** (line length 88, target `py314`). Don’t hand-format to a different style.
- **Linting**: prefer fixes that satisfy ruff rules rather than suppressing them.
  - Use `# noqa: <CODES>` only when justified and as narrow as possible.
- **Typing**: keep code **pyrefly-clean**.
  - Avoid `Any` and `cast()` unless bridging an external/untyped boundary (ASGI scope, framework hooks).
  - If an ignore is unavoidable, use the narrowest form (e.g. `# type: ignore[code]`) and keep it close to the boundary.

## 2.1) Style & Comments
- Follow PEP 8/PEP 257 conventions as enforced by ruff.
- Keep formatting consistent with the existing file; don’t “beautify” unrelated code.
- Minimize comments. Add them only when intent/invariants are not obvious from the code.

## 3) Repo Constraints (Don’t Fight the Stack)
- **Python**: `>=3.14` (use modern syntax, but don’t “upgrade” patterns just because you can).
- **Dependencies**: managed with `uv` (`uv.lock`). Do not add packages without explicit permission.
- **Repo boundaries**:
  - Backend logic stays in `backend/`. Do not import from `frontend/` into backend code.
- **Backend stack (when touching `backend/`)**:
  - **Litestar** (prefer `async def` for IO code)
  - **Strawberry GraphQL** + `strawberry.litestar`
  - **Advanced Alchemy / SQLAlchemy (async)** + Postgres (`asyncpg`)
  - **pydantic-settings (Pydantic v2)** for configuration

## 4) Modern Typing (Accurate, Not Performative)
- All public functions/methods should have type hints that reflect real runtime behavior.
- Prefer modern forms:
  - `X | Y` unions
  - built-in generics (`list[str]`, `dict[str, object]`)
  - `collections.abc` for `Iterable`, `Mapping`, `Callable`, etc.
- Don’t “type for the checker” by lying about types. If a value is dynamic, model it explicitly (e.g. `TypedDict`, `Protocol`) or keep it local and validate.
- Avoid `from __future__ import annotations` unless the file already uses it or the task requires it.

## 5) Async + Resource Safety by Default
- Use `async def` for request/DB/IO code in the backend.
- Use context managers (`with` / `async with`) for sessions, files, locks, etc.
- Avoid blocking calls in async paths (file IO, CPU-heavy hashing, network calls) unless explicitly accepted by the task.

## 6) Database Rules (Advanced Alchemy / SQLAlchemy Async)
- Prefer existing session acquisition patterns (e.g. `alchemy_config.get_session()` or injected `AsyncSession`).
- Keep transactions explicit and consistent:
  - Use `flush()` when you need DB-generated values during the request/resolver.
  - Use `commit()` only when you truly mean to finalize changes (follow existing patterns in the module).
- Prefer SQLAlchemy expressions (`select(...)`) over raw SQL unless required.
- Any schema/model change should be accompanied by the migration workflow (don’t mutate DB state manually).

## 6.1) Configuration / Settings (Pydantic v2)
- Don’t introduce new **required** env vars casually.
- If you add/change settings, update the `Settings` model, and keep setup docs/examples in sync (e.g. root README, `.env.example`, `backend/.env.example`) when applicable.

## 7) Strawberry GraphQL Rules (Schema & Contracts)
- Keep GraphQL **types/queries/mutations/inputs** in their existing modules under `backend/src/backend/apps/**/graphql/`.
- Resolvers should be thin; move multi-step workflows into a local `services.py` (within `backend/`) and call it.
- For user-visible errors, raise `GraphQLError` with a safe message. Don’t leak internals/tracebacks into GraphQL errors.
- Prefer typing the GraphQL context (e.g. `TypedDict`) over untyped stringly-typed dict access when practical.

## 8) Errors Must Not Disappear (With Narrow Exceptions)
- Do not swallow exceptions.
- Only catch exceptions you can handle meaningfully; otherwise re-raise.
- **Security boundary exception**: in auth/password verification, it can be acceptable to return a safe failure value instead of propagating unexpected exceptions, but:
  - keep the scope as narrow as possible
  - add a short justification if catching broadly

## 9) Logging vs Print
- Do not add `print()` for non-trivial codepaths.
- Prefer existing logging conventions in the area you’re editing. If none exist, use stdlib `logging` (don’t introduce new logging deps).
- Never log secrets (passwords, session secrets, tokens).

## 10) Docstrings (Only When They Add Signal)
- Add docstrings only for public APIs or non-obvious logic.
- Docstrings describe behavior, inputs/outputs, side effects, and exceptions (when relevant).
- Triple-quoted docstrings use `"""` (PEP 257).

## 11) Tests & Completion Bar
- Update/add tests when behavior changes (pytest + pytest-asyncio is in use).
- Before calling work “done” for backend changes, prefer the repo workflows:
  - `task backend:format`
  - `task backend:lint:fix`
  - `task backend:typecheck`
  - `task backend:test`
