---
description: TypeScript engineering rules (strict typing, ESM-first, repo-aligned, LLM-safe)
globs:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.mts"
  - "**/*.cts"
  - "**/*.d.ts"
alwaysApply: true
---

## 0) Prime Directive: No Guessing (LLM Safety)
- **In the face of ambiguity, refuse the temptation to guess.**
- If required context is missing (runtime: server vs client, caller expectations, types, invariants), **stop** and ask targeted questions rather than inventing it.
- Never invent modules, functions, env vars, CLI commands, or APIs that are not already present in the repo.
- Search before implementing:
  - Find an existing example in `frontend/src/**` that matches the task.
  - Reuse repo patterns (imports, naming, error handling, folder structure).

## 1) Type System First (Strictness & Boundaries)
- Prefer strict mode (`strict: true`). Do not loosen `frontend/tsconfig.json` (or add type escapes) unless explicitly asked.
- When introducing new TS config, keep these enabled: `noImplicitAny`, `noImplicitReturns`, `exactOptionalPropertyTypes`, `noUncheckedIndexedAccess`, `noFallthroughCasesInSwitch`.
- Use explicit types at module boundaries (exported functions/types, public methods, component props). Allow inference for locals.
- Prefer `unknown` over `any`; narrow with type guards. Avoid `as` unless the narrowing is proven; prefer `satisfies` and user-defined type predicates.
- Model nullability explicitly (`--strictNullChecks`). Avoid non-null assertions (`!`); narrow via control flow.
- Prefer discriminated unions over flag enums.
- Avoid `enum` by default in frontend code (runtime output + `isolatedModules` concerns). Prefer:
  - literal unions (`type Status = "open" | "closed"`)
  - `as const` objects (`const Status = { Open: "open" } as const`)
- Use `never` exhaustiveness checks for discriminated unions in `switch`/`if` chains.
- Use `readonly` for immutable props/tuples; use `as const` to stabilize literal inference where needed.
- Avoid ambient/global augmentations; prefer module-scoped types and explicit imports.

## 2) Modules & Structure
- Use ES modules (`import`/`export`) consistently; avoid mixing CommonJS unless required by the runtime.
- Use `import type` for type-only imports to avoid runtime side effects.
- One logical component or module per file; keep files focused and cohesive.
- Export a minimal, documented public surface; avoid exporting internal helpers unless part of the contract.
- Use index barrels only when they won't create circular deps; otherwise import directly.
- Avoid default exports in shared libraries.
  - Exception: Next.js App Router entrypoints commonly require/expect default exports (e.g. `src/app/**/page.tsx`, `layout.tsx`).

## 2.1) Repo Frontend Stack (frontend/)
- **Package manager**: `pnpm` (workspace). Use `pnpm` scripts or Taskfile tasks; never use npm/yarn to modify `pnpm-lock.yaml`.
- **Runtime/framework**: Node.js >=24, Next.js 16 (App Router), React 19.
  - Default to Server Components; use `"use client"` only when state/effects/browser APIs are required.
  - Keep Client Components as leaf nodes and place `"use client"` at the top of the file.
  - Follow `src/app` conventions (`layout.tsx`, `page.tsx`, `loading.tsx`, `error.tsx`).
- **Dev server**: `next dev --turbopack`; avoid Webpack-specific assumptions unless explicitly configured.
- **Styling**: Tailwind CSS 4 via `@tailwindcss/postcss` (`postcss.config.mjs`). Prefer utility classes; avoid custom CSS unless required.
- **Project structure**:
  ```
  src/
  ├── app/          # Routing only (page, layout, loading, error)
  ├── features/     # Domain modules with business logic + GraphQL + Stories
  ├── components/   # Shared UI (no business logic, no GraphQL)
  ├── lib/          # Utilities and providers
  ```
  - `features/` contains domain logic: GraphQL operations, state, business rules, stories. Example: `features/users/`.
  - `components/` contains pure UI: just props in, JSX out. Can be used by any feature. Example: `components/ui/ErrorMessage.tsx`.
  - `components/` must NOT import from `features/`. Dependency flows: `features/ → components/`, never reverse.
  - Colocate tests and stories with components: `UserCard.client.tsx`, `UserCard.test.tsx`, `UserCard.stories.tsx`.
  - For Storybook structure recommendations, see: https://storybook.js.org/blog/structuring-your-storybook/
  - For writing stories, see: https://storybook.js.org/docs/writing-stories
  - Colocate GraphQL operations with features: `features/users/GetUserById.graphql`.
- **GraphQL**: Apollo Client + `@apollo/client-integration-nextjs`.
  - Server data: `frontend/src/lib/apollo/client.server.ts`; client data: `frontend/src/lib/apollo/provider.client.tsx`.
  - Keep operations in `.graphql` files; run `pnpm codegen` (or `task frontend:codegen`) to regenerate types.
  - Do not edit generated code under `frontend/src/lib/graphql/**`.
  - Prefer generated documents + types from `@/lib/graphql/graphql` (e.g. `GetUserByIdDocument`, `GetUserByIdQuery`); do not hand-write GraphQL result types.
  - Import hooks from `@apollo/client/react` (not `@apollo/client`) due to Turbopack bundler resolution issues.
  - PreloadQuery pattern (doc-only example, uses real repo query):
    ```tsx
    // src/app/page.tsx (RSC)
    import { Suspense } from "react";
    import { PreloadQuery } from "@/lib/apollo/client.server";
    import { GetUserByIdDocument } from "@/lib/graphql/graphql";
    import UserCard from "@/features/users/UserCard.client";

    export default function Page() {
      return (
        <PreloadQuery query={GetUserByIdDocument} variables={{ userId: "1" }}>
          <Suspense fallback={<div>Loading user...</div>}>
            <UserCard userId="1" />
          </Suspense>
        </PreloadQuery>
      );
    }
    ```
    ```tsx
    // src/features/users/UserCard.client.tsx (Client Component)
    "use client";

    import { useSuspenseQuery } from "@apollo/client/react";
    import { GetUserByIdDocument } from "@/lib/graphql/graphql";

    function hasErrorCode(error: unknown, code: string): boolean {
      if (!error || typeof error !== "object") return false;
      const graphQLErrors = (error as { graphQLErrors?: unknown[] }).graphQLErrors;
      if (!Array.isArray(graphQLErrors)) return false;
      return graphQLErrors.some(
        (e) => e?.extensions?.code === code,
      );
    }

    export default function UserCard({ userId }: { userId: string }) {
      const { data, error } = useSuspenseQuery(GetUserByIdDocument, {
        variables: { userId },
        errorPolicy: "all",
      });

      const isNotFound = hasErrorCode(error, "NOT_FOUND");
      if (error && !isNotFound) return <p>Error: {error.message}</p>;
      if (!data?.user) return <p>User not found.</p>;

      return <div>{data.user.email}</div>;
    }
    ```
  - Mutation pattern (doc-only example, uses real repo mutation):
    ```tsx
    // src/features/users/UserCreator.client.tsx (Client Component)
    "use client";

    import { useMutation } from "@apollo/client/react";
    import {
      CreateUserDocument,
      type CreateUserMutationVariables,
    } from "@/lib/graphql/graphql";

    type CreateUserInput = CreateUserMutationVariables["userInput"];

    export default function UserCreator() {
      const [createUser, { data, loading, error }] = useMutation(CreateUserDocument, {
        errorPolicy: "all",
      });

      const handleCreate = async (input: CreateUserInput) => {
        try {
          const result = await createUser({ variables: { userInput: input } });
          return result.data?.createUser;
        } catch {
          // Hook's `error` state handles display; avoid unhandled rejections.
        }
      };

      if (loading) return <p>Creating...</p>;
      if (error) return <p>Error: {error.message}</p>;
      if (data?.createUser) return <p>Created: {data.createUser.email}</p>;

      return <button onClick={() => handleCreate({ ... })}>Create User</button>;
    }
    ```
  - Note: There is no `PreloadMutation`. Mutations are side-effects and run only from user actions or server actions. For server-side mutations, use `getClient().mutate()` inside a server action.
- **Tooling**: Biome for lint/format (`pnpm check`). Typecheck with `pnpm check:types`.
- **Testing**: Vitest (unit/component), Storybook 10 (`@storybook/nextjs-vite`) with story tests, Playwright for E2E.

## 3) Functions, Classes, and Data
- Favor pure functions; keep side effects explicit. Avoid hidden I/O or mutation.
- Use `interface` for contracts and `type` for composition/unions; keep both small and composable.
- Prefer composition over inheritance; use classes mainly for stateful domain objects or framework constraints.
- Avoid overloads in favor of discriminated unions; if overloading, keep signatures minimal and aligned with runtime behavior.
- Validate inputs at boundaries (API handlers, CLI args, components) and reflect validation in types where possible.

## 4) Async, Errors, and Resource Safety
- Use `async`/`await`; wrap cleanup in `try/finally`. Use `AbortController` for cancellation when supported.
- Never leave floating promises; `await` or explicitly handle fire-and-forget with a clear comment.
- Use typed results for expected failures; reserve `throw` for truly exceptional cases.
- Propagate errors with context; preserve stacks; never silently swallow errors.

## 5) Collections & Immutability
- Prefer immutable updates for arrays/maps/objects; mutate only when performance-critical and isolated.
- Use `Map`/`Set` over object dictionaries when keys aren't simple strings.
- Prefer `readonly` arrays/tuples in public APIs to signal immutability.

## 6) Naming & Style
- Descriptive identifiers; avoid abbreviations.
- Functions: verb-noun; types/interfaces: noun/adjective.
- Boolean flags start with `is`/`has`/`should`/`can`.
- Casing: `camelCase` for vars/functions, `PascalCase` for types/classes, `UPPER_SNAKE` for constants.

## 7) Documentation & Comments
- JSDoc for public APIs (params/returns, units, side effects, throws).
- Document invariants and preconditions (e.g., sorted arrays).
- Comments explain "why," not "what." Keep comments minimal and relevant.

## 8) Testing & Quality
- Prefer deterministic tests; isolate time/randomness via injection.
- Use type-level tests for complex utility types (e.g., `tsd`/`expect-type`) when needed.
- Keep snapshots small and intentional; favor explicit assertions.

## 9) Tooling & tsconfig Hygiene
- Use repo formatting/linting (Biome in `frontend/`). Don't introduce ESLint/Prettier unless explicitly required by the task.
- Do not change `frontend/tsconfig.json` compiler options unless explicitly requested.
- `tsconfig` hygiene (when creating new TS projects/packages): exclude build artifacts, set `rootDir`/`outDir` when emitting, enable incremental builds.
- Avoid new path aliases that obscure module boundaries unless already established; keep them minimal and documented.
- Emit targets/modules should match the runtime; don't downlevel features you don't test.
- Keep tree-shaking friendly: avoid side-effectful top-level code; declare `"sideEffects": false` only when valid.
- Repo note: `frontend/tsconfig.json` uses `strict`, `noEmit`, `moduleResolution: bundler`, and the `@/*` alias. Don't loosen these without a strong reason.

## 10) Security & Robustness
- Validate external data (API payloads, env vars) with schema validators and align runtime schema with TS types.
- Avoid stringly-typed APIs; prefer literal unions.
- Sanitize/encode when handling HTML/URLs; avoid unsafe HTML injections.
- Handle boundary cases: empty inputs, large payloads, timeouts, partial failures.

## 11) Performance
- Measure before optimizing; prefer readability until profiling indicates hotspots.
- Avoid unnecessary allocations in tight loops; use iterators/generators thoughtfully.
- Leverage `readonly` arrays/tuples to enable better compiler optimizations.

## 12) Interop & Ecosystem
- Prefer native ESM packages; use `esModuleInterop`/`allowSyntheticDefaultImports` only when necessary.
- Prefer platform APIs over polyfills; if polyfilling, be explicit about target environments and bundle size.

## 13) Generated Code Guidance (LLM)
- Prefer small, localized diffs that match existing patterns in the repo.
- Always include imports; avoid undeclared globals.
- Emit strict, typed signatures; narrow types instead of loosening (avoid `any`/broad assertions).
- Do not edit generated code (e.g. `frontend/src/lib/graphql/**`) or manually edit lockfiles.
- Do not introduce new tooling (ESLint/Prettier) or change `frontend/tsconfig.json` unless explicitly requested.
- Keep error handling explicit; no swallowed errors, no floating promises.
- Avoid `// @ts-ignore`; if a suppression is unavoidable, use `// @ts-expect-error` with a short reason.
