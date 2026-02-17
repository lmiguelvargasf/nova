---
name: update-frontend-dependency
description: Update a frontend dependency to the latest stable version with Taskfile wrappers.
---

Follow repo rules in:

- .github/instructions/frontend.instructions.md

Task:

- Confirm the dependency already exists in `frontend/package.json` under
  `dependencies` or `devDependencies`; if it does not, stop and ask before
  adding a new dependency.
- Resolve the latest stable version for the requested dependency from the npm
  registry (source of truth) immediately before running any update command.
- Do not infer "latest" from `frontend/pnpm-lock.yaml`, current
  `frontend/package.json` constraints, or local pnpm cache.
- Preserve the existing version range style (`^`, `~`, or exact) unless the
  request explicitly asks to change it.
- From project root, run one command:
  - `task frontend:dep:add -- "<dependency>@<updated_specifier>"`
  - `task frontend:dep:add:dev -- "<dependency>@<updated_specifier>"`
- Do not manually edit dependency files; let `pnpm add` update them.
- Run `task frontend:install` only if an additional install/sync is needed.

Constraints:

- Keep changes minimal and scoped.
- Update only the requested dependency unless explicitly asked to update more.
- Keep dependency name unchanged; only move the version inside its existing
  specifier style.
- Prefer stable releases; use pre-releases only when explicitly requested.
- If npm registry cannot be reached or the latest stable version cannot be
  determined, stop and report the blocker instead of guessing.

Output:

- List changed tracked files.
- Expected files: `frontend/package.json` and `frontend/pnpm-lock.yaml` (explain
  extras).
- Include the resolved latest version, npm source used, and the exact Taskfile
  command used.
- If no files changed, explicitly report that the dependency was already at the
  latest version for its existing range style.
