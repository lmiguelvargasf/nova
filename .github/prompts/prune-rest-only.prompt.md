---
name: prune-rest-only
description: Keep only a minimal backend REST template (no GraphQL/frontend/iOS/celery/redis).
---

Task:

- Run `task template:prune:rest-only`.
- Run `task template:prune:validate -- rest-only`.
- Create branch/commit/push using Taskfile wrappers:
  - `task git:branch -- codex/nova-prune-rest-only`
  - `task git:commit -- "refactor: prune template to rest-only"`
  - `task git:push`
- Create PR with `.github/prompts/pr-creation.prompt.md`.

Constraints:

- Do not run raw destructive commands; Taskfile targets are the source of truth.
- Stop if prune guardrails fail (dirty tree, main branch, confirmation denied).

Output:

- List files changed.
- Include commands executed.
- Include PR URL.
