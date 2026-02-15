# AGENTS.md

## General Instruction

- Use tasks defined in [Taskfile.yml](Taskfile.yml) as the source
  of truth for running project commands.
- Do not invent commands. If a needed operation is not represented
  as a task, call that out explicitly and ask whether to add a task
  first.

## Canonical Rule Source

- Canonical coding policies live in [`.github/instructions/`](.github/instructions/).
- `AGENTS.md` files are cross-agent adapters and should reference canonical
  instruction files instead of duplicating their policy bodies.

## Routing by Path

- `backend/`: apply
  [`.github/instructions/backend.instructions.md`](.github/instructions/backend.instructions.md)
  and
  [`.github/instructions/python.instructions.md`](.github/instructions/python.instructions.md).
- `frontend/`: apply
  [`.github/instructions/frontend.instructions.md`](.github/instructions/frontend.instructions.md)
  and
  [`.github/instructions/typescript.instructions.md`](.github/instructions/typescript.instructions.md).
- `ios/`: apply
  [`.github/instructions/swiftui.instructions.md`](.github/instructions/swiftui.instructions.md).

## Precedence and Conflicts

- The most specific `AGENTS.md` in scope applies first (for example,
  `backend/AGENTS.md` over this file for backend paths).
- Avoid policy duplication across `AGENTS.md` and
  `.github/instructions/*.instructions.md`.
