---
name: update-mise-dependencies
description: Update all mise-managed dependencies, validate setup, and open a PR.
---

Task:

- Create a Linear issue in team `nova` and project `Support for Codex` for the
  update work.
- Create a branch from `main` using the issue id and `codex/` prefix (for example,
  `codex/NOVA-123-update-mise-dependencies`).
- Find the latest version for each tool in `mise.toml` with `mise latest <tool>`.
- For Node.js, use the latest LTS version with `mise latest node@lts` (not the
  development line).
- Update `mise.toml` for each dependency that has a newer target version.
- Commit each dependency upgrade separately (one commit per dependency).
- Run `./setup.sh` and confirm it completes successfully.
- Push the branch.
- Create a PR using `.github/prompts/pr-creation.prompt.md`.
- Reference the Linear issue in the PR body.

Constraints:

- Keep changes minimal and scoped to `mise` dependency updates.
- Do not create no-op commits for dependencies already at the target version.
- Keep commit messages explicit, e.g.:
  - `chore(mise): bump <tool> to <version>`
  - `chore(mise): use latest node lts <version>` for Node LTS changes

Output:

- Linear issue URL.
- Final `mise.toml` tool versions.
- List of commits created.
- PR URL.
