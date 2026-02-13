---
name: update-mise-dependencies
description: Update all mise-managed dependencies and validate setup.
---

Task:

- Find the latest version for each tool in `mise.toml` with `mise latest <tool>`.
- For Node.js, use the latest LTS version with `mise latest node@lts` (not the
  development line).
- Update `mise.toml` for each dependency that has a newer target version.
- Commit each dependency upgrade separately (one commit per dependency).
- Run `./setup.sh` and confirm it completes successfully.

Constraints:

- Keep changes minimal and scoped to `mise` dependency updates.
- Do not create no-op commits for dependencies already at the target version.
- Keep commit messages explicit, e.g.:
  - `chore(mise): bump <tool> to <version>`
  - `chore(mise): use latest node lts <version>` for Node LTS changes

Output:

- Final `mise.toml` tool versions.
