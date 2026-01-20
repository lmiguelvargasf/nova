---
name: update-pnpm
description: Update pnpm version across the repo.
---

Follow the repo rules in:

- .github/instructions/frontend.instructions.md

Task:

- Find the latest pnpm version
- Update mise.toml to use the latest pnpm version.
- Update .github/actions/frontend-setup/action.yaml to use the latest pnpm
  version.
- Update frontend/package.json `packageManager` to the latest pnpm version.

Constraints:

- Keep changes minimal.
- Keep pnpm versions consistent across all updated files.

Output:

- List files changed.
- List latest pnpm version used.
