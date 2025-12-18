---
description: Canonical dev workflow (Taskfile-first). Taskfile is the single source of truth for running this repo.
alwaysApply: true
---

## 0) Prime Directive
This repo is **Taskfile-first** for workflow operations (install/dev/build/lint/format/test/codegen/docker lifecycle).
- Prefer `task <target>` over raw `docker`, `docker compose`, `pnpm`, `pip`, `uv`, etc.
- It’s OK to use raw commands for **read-only diagnostics** (e.g., `ls`, `cat`, `grep`, `curl`) when they don’t replace a workflow.
- Diagnostics that don’t replace a workflow (e.g., logs/status/version checks) may be run directly when helpful.
- Never invent task targets. If you're not sure a target exists, **verify first**.

## 1) Discovery Protocol (Before suggesting any workflow command)
1. Inspect `Taskfile.yml` (and any `includes:` Taskfiles) to see real targets and docs.
2. If a workflow likely lives in a subdirectory, check for a local Taskfile and use `task -d <dir> <target>`.
3. If you can’t confidently verify targets from files:
   - Ask for `task --list` output (or `task --list-all`) and proceed from that.
4. Use safe inspection when helpful:
   - `task --list` to enumerate tasks
   - `task --summary <task>` to confirm what it does (no execution)

## 2) Execution Rules (How to run things)
- Always recommend the **Taskfile path**:
  - Docker lifecycle must go through Taskfile targets (no `docker compose up` directly). In this repo, Docker Compose handles just the database service.
  - Frontend install/dev/codegen must go through Taskfile targets.
- For unfamiliar tasks, prefer `task --summary <task>` before execution (safe, no-op).
- Only suggest raw commands when:
  1) there is no Task target **and**
  2) you will immediately propose adding a Task target to wrap it.
- If the user explicitly requests a raw workflow command, provide it as **non-canonical** and still propose the Taskfile wrapper.

## 3) Verification Rules (Definition of Done)
After suggesting a command, include:
- What success looks like (expected ports, generated files, or services up)
- The follow-up check to confirm it worked (usually another `task ...`)

Contract-sensitive changes:
- If backend GraphQL/schema changes: require running the repo’s codegen task afterwards.
- If env vars change: update `.env.example` (and service-specific examples) + README notes.

## 4) Maintenance (When a task is missing)
If a necessary workflow is missing from Taskfile:
- Do **not** provide a multi-step manual shell sequence as the “official way”.
- Propose adding a Task target in `Taskfile.yml` and then using it.

Naming convention for new tasks:
- `scope:action` (examples: `backend:test`, `frontend:lint`, `db:migrate`, `docker:up`)
- Prefer “verbs” for actions: `install`, `dev`, `test`, `lint`, `fmt`, `build`, `codegen`, `migrate`.

If you add a task:
- Update `README.md` “Quick start / Dev tasks” so Taskfile remains discoverable.

## 5) Safety (No foot-guns)
Never suggest or run destructive operations without explicit user confirmation:
- DB reset/drop, migrations that drop data, container prune, volume deletion, `--force`, etc.
If a task seems destructive, require: “Confirm yes/no” before proceeding.
