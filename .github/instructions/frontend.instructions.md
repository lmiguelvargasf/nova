---
applyTo:
  - "frontend/**/*"
  - "Taskfile.yml"
  - "compose.yaml"
---

# Frontend instructions

## Scope boundary

- Keep all frontend logic within `frontend/`. Do not import from `backend/`.
- Cross-repo changes are allowed only when required by the task or needed to keep contracts/examples in sync:
  - GraphQL schema/codegen outputs (e.g., `task backend:schema:export` / `task frontend:codegen`)
  - `.env.example` / README updates when frontend env vars or workflows change

## Technology stack & standards

- Framework: Next.js 16 (App Router).
- Runtime: Node.js 24.
- Styling: Tailwind CSS 4. Follow existing design tokens and utility patterns; avoid custom CSS unless necessary.
- Language: TypeScript with strict typing; avoid `any`.
- Package manager: `pnpm` (workspace + `pnpm-lock.yaml`). Do not add packages without explicit permission.
- Data fetching: Apollo Client (GraphQL). Use `src/lib/apolloClient.server.ts` for Server Components and `src/lib/apolloClient.ts` for Client Components.
- Linting/formatting: Biome; use `task frontend:check` for fixes.

## Conventions

- Follow existing Next.js conventions and project structure.
- Avoid drive-by refactors; change only what the task requires.

## Code organization

- `src/app/`: routes, layouts, `loading.tsx`, `error.tsx`.
- `src/components/`: reusable UI components.
- `src/lib/`: shared utilities, Apollo clients, GraphQL generated code.
- `src/stories/`: component documentation and story tests.

## Server vs Client Components

- Default to Server Components for data fetching and static content.
- Use `"use client"` only when state/effects/browser APIs are required.
- Place `"use client"` at the very top of the file.
- Keep Client Components as leaf nodes to maximize server rendering.

## GraphQL & contracts

- Update the backend schema first when API changes are needed.
- After schema changes, run `task frontend:codegen` to update types and hooks.
- Define `.graphql` files alongside components.
- Use fragment masking via `useFragment` from `src/lib/graphql/`; avoid passing large unmasked objects through props.

## Component development & testing

- Create stories for new UI components in `src/stories/` or alongside the component.
- Testing hierarchy:
  - Unit/Component: Vitest (`task frontend:test:run`).
  - Story tests: `task frontend:test:storybook`.
  - E2E: Playwright (`task frontend:test:e2e`).
- Implement `loading.tsx` and `error.tsx` for robust UX.

## Validation workflow

Before declaring a frontend task complete:

- Run `task frontend:format` and `task frontend:check`.
- Ensure `task frontend:test:run` and `task frontend:test:storybook` pass.
- If GraphQL was touched: ensure `task frontend:codegen` was run and no type errors exist.
- Verify accessibility and responsive behavior.
- Check `.env.example` if new environment variables were introduced.
