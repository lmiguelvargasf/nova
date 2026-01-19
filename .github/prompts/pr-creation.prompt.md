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

Output:

- Summarize the diff at a high level.
- Provide the PR URL.
- List any commands used.
