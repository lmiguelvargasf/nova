---
name: install-backend-dependency
description: Install a backend Python dependency with Taskfile wrappers.
---

Task:

- If the requested dependency does not include a version specifier, resolve the
  latest stable version from PyPI (source of truth) immediately before
  installing, then run one command:
  - `task backend:dep:add -- "<dependency>>=<latest_version>"`
  - `task backend:dep:add:dev -- "<dependency>>=<latest_version>"`
- If the request includes an explicit version/range, preserve it exactly and
  run one command:
  - `task backend:dep:add -- <dependency_with_specifier>`
  - `task backend:dep:add:dev -- <dependency_with_specifier>`
- Do not infer "latest" from `backend/uv.lock`, current `pyproject.toml`, or
  local environment cache.
- Do not manually edit dependency files; let `uv add` update them.
- Run `task backend:install` only if an additional environment sync is needed.

Constraints:

- Keep changes minimal and scoped.
- Install only the requested dependency unless explicitly asked to add more.
- Prefer stable releases; use pre-releases only when explicitly requested.
- If PyPI cannot be reached or the latest stable version cannot be determined
  (when required), stop and report the blocker instead of guessing.

Output:

- List changed tracked files.
- Expected files: `backend/pyproject.toml` and `backend/uv.lock` (explain extras).
- Include the exact Taskfile command used.
- When latest resolution was required, include the resolved version and the PyPI
  source used.
