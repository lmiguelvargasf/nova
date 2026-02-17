---
name: install-frontend-dependency
description: Install a frontend dependency with Taskfile pnpm wrappers.
---

Follow repo rules in:

- .github/instructions/frontend.instructions.md

Task:

- If the requested dependency does not include a version specifier, resolve the
  latest stable version from the npm registry (source of truth) immediately
  before installing, then run one command:
  - `task frontend:dep:add -- "<dependency>@<latest_version>"`
  - `task frontend:dep:add:dev -- "<dependency>@<latest_version>"`
- If the request includes an explicit version/range, preserve it exactly and
  run one command:
  - `task frontend:dep:add -- <dependency_with_specifier>`
  - `task frontend:dep:add:dev -- <dependency_with_specifier>`
- Do not infer "latest" from `frontend/pnpm-lock.yaml`, current
  `frontend/package.json`, or local pnpm cache.
- Do not manually edit dependency files; let `pnpm add` update them.
- Run `task frontend:install` only if an additional install/sync is needed.

Constraints:

- Keep changes minimal and scoped.
- Install only the requested dependency unless explicitly asked to add more.
- Prefer stable releases; use pre-releases only when explicitly requested.
- When no range was requested, keep pnpm's default save-prefix behavior.
- If npm registry cannot be reached or the latest stable version cannot be
  determined (when required), stop and report the blocker instead of guessing.

Output:

- List changed tracked files.
- Expected files: `frontend/package.json` and `frontend/pnpm-lock.yaml` (explain
  extras).
- Include the exact Taskfile command used.
- When latest resolution was required, include the resolved version and npm
  source used.
