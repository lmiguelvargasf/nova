---
name: prune-no-ios
description: Remove iOS template and iOS workflow wiring.
---

Task:

- Run `task template:prune:no-ios`.
- Run `task template:prune:validate -- no-ios`.
- Create branch/commit/push using Taskfile wrappers:
  - `task git:branch -- codex/nova-prune-no-ios`
  - `task git:commit -- "refactor: prune template to no-ios"`
  - `task git:push`
- Create PR with `.github/prompts/pr-creation.prompt.md`.

Constraints:

- Do not run raw destructive commands; Taskfile targets are the source of truth.
- Stop if prune guardrails fail (dirty tree, main branch, confirmation denied).

Output:

- List files changed.
- Include commands executed.
- Include PR URL.
