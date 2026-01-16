---
name: graphql-contract
description: Sync the GraphQL contract and codegen outputs.
---

Follow the repo rules in:

- .github/skills/graphql-contract/SKILL.md
- .github/instructions/backend.instructions.md
- .github/instructions/frontend.instructions.md

Task:

- Apply GraphQL changes in backend resolvers/types or frontend .graphql files.
- Run task frontend:codegen and update any affected frontend usage.
- Keep schema and generated types in sync.

Constraints:

- Do not edit frontend/schema/schema.graphql directly.
- Do not edit generated code under frontend/src/lib/graphql/.
- Keep changes minimal.

Output:

- List files changed.
- Include any Taskfile commands used.
