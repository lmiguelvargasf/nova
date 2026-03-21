---
name: clean-local-branches
description: Force-delete every local git branch except main and leave the repo on main.
---

Follow repo rules in:

- AGENTS.md
- .github/skills/workflow-taskfile/SKILL.md
- .github/skills/guardrails/SKILL.md

Task:

- Clean up local git branches so only `main` remains.
- Run this workflow from the repository root.

Steps:

1. Run the single-source cleanup workflow:

   ```bash
   task git:branches:clean:local
   ```

Constraints:

- Delete local branches only; do not delete `main`.
- Do not modify or delete remote branches.
- If switching to `main` fails because of local changes or conflicts, stop and
  report the blocker instead of forcing through it.

Output:

- Starting branch.
- Deleted local branches, or a note that none were present.
- Final local branch list.
