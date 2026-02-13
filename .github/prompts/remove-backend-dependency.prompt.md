---
name: remove-backend-dependency
description: Remove a backend Python dependency with Taskfile wrappers.
---

Task:

- From project root, run one command:
  - `task backend:dep:remove -- <dependency>`
  - `task backend:dep:remove:dev -- <dependency>`
- Do not manually edit dependency files; let `uv remove` update them.
- Run `task backend:install` only if an additional environment sync is needed.

Constraints:

- Keep changes minimal and scoped.
- Remove only the requested dependency unless explicitly asked to remove more.

Output:

- List changed tracked files.
- Expected files: `backend/pyproject.toml` and `backend/uv.lock` (explain extras).
- Include the exact Taskfile command used.
