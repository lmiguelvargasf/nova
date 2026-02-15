---
name: pr-creation
description: Create a pull request comparing the current branch to main.
---

Task:

- Compare the current branch against `main`.
- Create a pull request using Taskfile workflows, applying the template in
  `.github/pull_request_template.md`.

Constraints:

- Do not modify code unless explicitly asked.
- Keep changes minimal and scoped.
- Choose a semantic PR title that satisfies
  `.github/workflows/pr-validation.yml`:
  - Format: `<type>: <summary>` or `<type>(scope): <summary>`
  - Allowed `type` values:
    `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`,
    `ci`, `chore`, `revert`
- Read `.github/pull_request_template.md` and fill in the required sections.
- Write the completed body into a temporary file. For example:

  ```bash
  cat <<'EOF' > /tmp/prbody.md
  <rendered template>
  EOF
  ```

- When updating a PR body, run:

  ```bash
  task pr:edit -- <pr-number>
  ```

- When creating a PR, run:

  ```bash
  PR_TITLE="<type>: <summary>" task pr:create -- <branch>
  ```

- If `<branch>` is omitted, `task pr:create` defaults to the current branch:

  ```bash
  PR_TITLE="<type>: <summary>" task pr:create
  ```

Output:

- Provide the PR URL.
