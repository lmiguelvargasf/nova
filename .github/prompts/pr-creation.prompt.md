---
name: pr-creation
description: Create a pull request comparing the current branch to main.
---

Task:

- Compare the current branch against `main`.
- Create a pull request using `gh`, applying the template in
  .github/pull_request_template.md.

Constraints:

- Do not modify code unless explicitly asked.
- Keep changes minimal and scoped.
- Read `.github/pull_request_template.md` and fill in the required sections.
- Write the completed body into a temporary file. For example:

  ```bash
  cat <<'EOF' > /tmp/prbody.md
  <rendered template>
  EOF
  ```

- When updating a PR body, run:

  ```bash
  gh pr edit <pr-number> --body "$(cat /tmp/prbody.md)"
  ```

- When creating a PR, run:

  ```bash
  gh pr create --base main --head <branch> --body "$(cat /tmp/prbody.md)"
  ```

Output:

- Provide the PR URL.
