---
description: TypeScript engineering rules (strict typing, ESM-first, repo-aligned)
globs:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.mts"
  - "**/*.cts"
  - "**/*.d.ts"
alwaysApply: true
---

## 0) Prime Directive: No Guessing
- **In the face of ambiguity, refuse the temptation to guess.**
- If required context is missing (caller expectations, types, invariants, runtime environment), **stop** and ask for what's missing rather than inventing it.
- Never invent modules, functions, env vars, CLI commands, or APIs that are not already present in the repo.

## 1) Type System First (Strictness & Boundaries)
- Prefer strict mode (`strict: true`) and keep these on when `tsconfig` is in scope: `noImplicitAny`, `noImplicitReturns`, `exactOptionalPropertyTypes`, `noUncheckedIndexedAccess`, `noFallthroughCasesInSwitch`.
- Use explicit types at module boundaries (exported functions/types, public methods, component props). Allow inference for locals.
- Prefer `unknown` over `any`; narrow with type guards. Avoid `as` unless the narrowing is proven; prefer `satisfies` and user-defined type predicates.
- Model nullability explicitly (`--strictNullChecks`). Avoid non-null assertions (`!`); narrow via control flow.
- Prefer discriminated unions over flag enums. Avoid `enum`; use literal unions, or `const enum` only when safe and tree-shakable.
- Use `never` exhaustiveness checks for discriminated unions in `switch`/`if` chains.
- Use `readonly` for immutable props/tuples; use `as const` to stabilize literal inference where needed.
- Avoid ambient/global augmentations; prefer module-scoped types and explicit imports.

## 2) Modules & Structure
- Use ES modules (`import`/`export`) consistently; avoid mixing CommonJS unless required by the runtime.
- Use `import type` for type-only imports to avoid runtime side effects.
- One logical component or module per file; keep files focused and cohesive.
- Export a minimal, documented public surface; avoid exporting internal helpers unless part of the contract.
- Use index barrels only when they won't create circular deps; otherwise import directly.

## 2.1) Repo Frontend Stack (frontend/)
- **Package manager**: `pnpm` (workspace). Use `pnpm` scripts or Taskfile tasks; never use npm/yarn to modify `pnpm-lock.yaml`.
- **Runtime/framework**: Node.js >=24, Next.js 16 (App Router), React 19.
  - Default to Server Components; use `"use client"` only when state/effects/browser APIs are required.
  - Keep Client Components as leaf nodes and place `"use client"` at the top of the file.
  - Follow `src/app` conventions (`layout.tsx`, `page.tsx`, `loading.tsx`, `error.tsx`).
- **Dev server**: `next dev --turbopack`; avoid Webpack-specific assumptions unless explicitly configured.
- **Styling**: Tailwind CSS 4 via `@tailwindcss/postcss` (`postcss.config.mjs`). Prefer utility classes; avoid custom CSS unless required.
- **GraphQL**: Apollo Client + `@apollo/client-integration-nextjs`.
  - Server data: `frontend/src/lib/apolloClient.server.ts`; client data: `frontend/src/lib/apolloClient.ts`.
  - Keep operations in `.graphql` files; run `pnpm codegen` (or `task frontend:codegen`) to regenerate types.
  - Use generated types from `frontend/src/lib/graphql`; do not hand-write GraphQL result types.
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
- Avoid default exports in shared libraries; prefer named exports for refactoring/tooling.

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
- `tsconfig` hygiene: exclude build artifacts, set `rootDir`/`outDir` when emitting, enable incremental builds.
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
- Always include imports; avoid undeclared globals.
- Emit strict, typed function signatures; narrow types instead of loosening.
- Add minimal, relevant JSDoc for exported items.
- Provide small, focused modules with cohesive responsibilities.
- Keep error handling explicit; don't swallow errors.
- Default to immutable patterns; avoid mutation unless justified.
- Ensure code is lint-friendly (no unused vars/params, consistent return types).
- Include type-safe async flows with `await` and proper error propagation.
- Avoid `// @ts-ignore`; if a suppression is unavoidable, use `// @ts-expect-error` with a short reason.
