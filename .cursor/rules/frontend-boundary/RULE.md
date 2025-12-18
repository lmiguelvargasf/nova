---
description: Frontend boundary rules (Next.js 15, TypeScript, Tailwind 4, Apollo)
alwaysApply: true
---

## 1) Technology Stack & Standards
- **Framework**: Next.js 15 (App Router).
- **Styling**: Tailwind CSS 4. Follow existing design tokens and utility patterns. Avoid custom CSS unless absolutely necessary.
- **Language**: TypeScript. Maintain strict typing; avoid `any`.
- **Data Fetching**: Apollo Client (GraphQL). Use `src/lib/apolloClient.server.ts` for Server Components and `src/lib/apolloClient.ts` for Client Components.
- **Linting & Formatting**: Biome is the primary tool. Use `task frontend:check` for automated fixes.

## 2) Scope Boundary
- **Isolation**: Keep all frontend logic within `frontend/`. Never import from `backend/`.
- **Structure**:
  - `src/app/`: Next.js pages, layouts, `loading.tsx`, and `error.tsx`.
  - `src/components/`: Reusable UI components.
  - `src/lib/`: Shared utilities, Apollo clients, and GraphQL generated code.
  - `src/stories/`: Component documentation and story tests.
- **Dependencies**: Use `pnpm` for dependency management. Avoid adding new packages without explicit justification.

## 3) Server vs Client Components
- **Default to Server Components**: Use them for data fetching and static content by default.
- **'use client'**: Only use when state (`useState`, `useReducer`), effects (`useEffect`), or browser-only APIs are required.
- **Placement**: Place `'use client'` at the very top of the file.
- **Boundary Strategy**: Keep Client Components as leaf nodes whenever possible to maximize server rendering.

## 4) GraphQL & Contracts
- **Schema First**: Update the backend schema first when API changes are needed.
- **Codegen**: After backend schema changes, run `task frontend:codegen` to update frontend types and hooks.
- **Queries/Mutations**: Define `.graphql` files alongside components (e.g., `src/components/MyComponent/MyQuery.graphql`).
- **Fragment Masking**: Use `useFragment` from `src/lib/graphql/` to consume data. Avoid passing large, unmasked objects through component props.

## 5) Component Development & Testing
- **Storybook**: Create stories for new UI components in `src/stories/` or alongside the component.
- **Testing Hierarchy**:
  - **Unit/Component**: Use Vitest (`task frontend:test:run`). Focus on logic and rendering.
  - **Story Tests**: Use `task frontend:test:storybook`. Focus on visual regressions and accessibility in isolation.
  - **E2E**: Use Playwright (`task frontend:test:e2e`). Focus on critical user flows.
- **Loading & Errors**: Implement `loading.tsx` (skeleton states) and `error.tsx` for a robust UX.

## 6) Validation Workflow
Before declaring a frontend task complete:
1. Run `task frontend:format` and `task frontend:check`.
2. Ensure `task frontend:test:run` and `task frontend:test:storybook` pass.
3. If GraphQL was touched: ensure `task frontend:codegen` was run and no type errors exist.
4. Verify accessibility (A11y) and responsive behavior across screen sizes.
5. Check `.env.example` if new environment variables were introduced.
