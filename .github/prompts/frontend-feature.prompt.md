---
name: frontend-feature
description: Add a frontend feature in Next.js App Router with GraphQL and
  tests.
---

Follow the repo rules in:

- .github/instructions/frontend.instructions.md
- .github/instructions/typescript.instructions.md

Task:

- Add a feature under frontend/src/features/{feature}/ and the route in
  frontend/src/app/.
- Use GraphQL .graphql documents and generated hooks.
- Add component tests (Vitest) and, if appropriate, a Storybook story.

Constraints:

- Keep Server Components by default; use "use client" only if needed.
- Do not edit generated code directly.

Output:

- List files changed.
- Include any Taskfile commands used.
