---
name: backend-entity
description: Create a backend entity (model, service, GraphQL, admin view, migration).
---

Follow the repo rules in:

- .github/instructions/backend.instructions.md
- .github/instructions/python.instructions.md

Task:

- Add a new entity in backend/src/backend/apps/{domain}/ using the required
  structure.
- Include GraphQL types/inputs/queries/mutations and admin view registration.
- If models change, create a migration and describe how to apply it using
  Taskfile targets.

Constraints:

- Do not add dependencies.
- Keep changes minimal.
- If GraphQL schema changes, run task frontend:codegen and note any updated
  files.

Output:

- List files changed.
- Include any Taskfile commands used.
