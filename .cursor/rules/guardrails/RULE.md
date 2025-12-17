---
description: Repo-wide guardrails for safe, consistent changes
alwaysApply: true
---

## Change discipline
- Prefer **small, incremental changes** over large or sweeping edits.
- Avoid refactoring or reformatting unrelated code.
- Don’t invent architecture; follow existing patterns and conventions in the repo.

## Validation before completion
- Before finishing a task, ensure relevant **linters, formatters, and tests pass locally** (or via Taskfile if available).
- If changing behavior, add or update tests accordingly.

## Safety & scope
- Never commit secrets or real credentials (including in `.env*`); use `.env.example`.
- Avoid cross-cutting backend + frontend changes unless explicitly required.

## When uncertain
- Inspect nearby code and mirror existing patterns.
- If the task is non-trivial, propose a short step plan before implementing.
