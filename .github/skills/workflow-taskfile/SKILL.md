---
name: workflow-taskfile
description: Use when running installs, dev servers, tests, lint/format, codegen, or Docker lifecycle tasks; Taskfile is the source of truth.
---

# Workflow: Taskfile-first

## When to use

- You need to install, run dev servers, lint/format, test, build, run codegen, or manage Docker lifecycle.
- You are unsure whether a workflow task exists.

## Steps

1. Inspect `Taskfile.yml` (and included Taskfiles) to confirm valid targets.
2. If the workflow likely lives in a subdirectory, check for a local Taskfile and use `task -d <dir> <target>`.
3. If you cannot confirm a target, ask for `task --list` or `task --list-all` output.
4. Prefer `task <target>` over raw commands for workflows.
5. For unfamiliar tasks, use `task --summary <task>` before execution.

## Constraints and guardrails

- Do not invent task targets.
- Use raw commands only for read-only diagnostics unless you are also proposing a Taskfile wrapper.
- Do not recommend destructive operations (DB reset/drop, prune, `--force`, volume deletion) without explicit confirmation.
- If a required workflow is missing, add a Taskfile target and update README “Quick start / Dev tasks.”

## References

- `Taskfile.yml`
- `backend/Taskfile.yml`
- `frontend/Taskfile.yml`
