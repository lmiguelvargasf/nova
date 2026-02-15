---
name: prune-no-rest
description: Prune REST components and keep GraphQL stack.
---

Task:

- Run `task template:prune:no-rest`.
- Run `task template:prune:validate -- no-rest`.
- Create branch/commit/push using Taskfile wrappers:
  - `task git:branch -- codex/nova-prune-no-rest`
  - `task git:commit -- "refactor: prune template to no-rest"`
  - `task git:push`
- Create PR with `.github/prompts/pr-creation.prompt.md`.

Constraints:

- Do not run raw destructive commands; Taskfile targets are the source of truth.
- Stop if prune guardrails fail (dirty tree, main branch, confirmation denied).

Output:

- List files changed.
- Include commands executed.
- Include PR URL.
