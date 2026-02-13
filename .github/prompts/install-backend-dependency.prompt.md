---
name: install-backend-dependency
description: Install a backend Python dependency with Taskfile wrappers.
---

Task:

- From project root, run one command:
  - `task backend:dep:add -- <dependency>`
  - `task backend:dep:add:dev -- <dependency>`
- Do not manually edit dependency files; let `uv add` update them.
- Run `task backend:install` only if an additional environment sync is needed.

Constraints:

- Keep changes minimal and scoped.
- Install only the requested dependency unless explicitly asked to add more.

Output:

- List changed tracked files.
- Expected files: `backend/pyproject.toml` and `backend/uv.lock` (explain extras).
- Include the exact Taskfile command used.
