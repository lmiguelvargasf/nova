---
name: update-backend-dependency
description: Update a backend Python dependency to a >= latest minimum version.
---

Task:

- Confirm the dependency already exists in `backend/pyproject.toml`; if it does
  not, stop and ask before adding a new dependency.
- Resolve the latest stable version for the requested dependency.
- From project root, run one command:
  - `task backend:dep:add -- "<dependency>>=<latest_version>"`
  - `task backend:dep:add:dev -- "<dependency>>=<latest_version>"`
- Do not manually edit dependency files; let `uv add` update them.
- `uv add` already syncs the environment; run `task backend:install` only if an
  extra sync is needed.

Constraints:

- Keep changes minimal and scoped.
- Update only the requested dependency unless explicitly asked to update more.
- Keep dependency name/extras unchanged; only move the minimum version floor.
- Prefer stable releases; use pre-releases only when explicitly requested.

Output:

- List changed tracked files.
- Expected files: `backend/pyproject.toml` and `backend/uv.lock` (explain
  extras).
- Include the resolved latest version and the exact Taskfile command used.
- If no files changed, explicitly report that the dependency was already at the
  latest minimum version.
