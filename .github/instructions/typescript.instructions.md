---
applyTo:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.mts"
  - "**/*.cts"
  - "**/*.d.ts"
---

# TypeScript instructions

## Prime directive: no guessing
- If required context is missing (runtime: server vs client, caller expectations, types, invariants), stop and ask targeted questions.
- Never invent modules, functions, env vars, CLI commands, or APIs that are not already present in the repo.
- Search before implementing: find an existing example in `frontend/src/**` and reuse repo patterns.

## Type system first
- Keep strict mode; do not loosen `frontend/tsconfig.json` or add type escapes unless asked.
- Use explicit types at module boundaries; allow inference for locals.
- Prefer `unknown` over `any` and narrow with type guards.
- Model nullability explicitly; avoid non-null assertions and `as` unless proven.
- Prefer discriminated unions and `never` exhaustiveness checks.
- Avoid `enum` by default; use literal unions or `as const` objects.
- Use `readonly` for immutable props/tuples.
- Avoid ambient/global augmentations; prefer module-scoped types.

## Modules & structure
- Use ES modules consistently; use `import type` for type-only imports.
- One logical component/module per file; keep files focused.
- Export a minimal public surface; avoid index barrels that create circular deps.
- Avoid default exports in shared libraries (Next.js app entrypoints are the exception).

## Frontend stack (frontend/)
- Package manager: `pnpm` workspace. Use `pnpm` scripts or Taskfile targets.
- Runtime/framework: Node.js >=24, Next.js 16 (App Router), React 19.
- Default to Server Components; use `"use client"` only when required and place it at the top.
- Styling: Tailwind CSS 4; prefer utility classes.
- Project structure:
  - `src/app/` for routing
  - `src/features/` for domain logic + GraphQL + stories
  - `src/components/` for shared UI (no business logic, no GraphQL)
  - `src/lib/` for utilities/providers
  - Dependency flow: `features/ → components/` only
- GraphQL:
  - Use `.graphql` files and run `task frontend:codegen` to regenerate types.
  - Do not edit generated code under `frontend/src/lib/graphql/**`.
  - Import hooks from `@apollo/client/react` (Turbopack resolution).
  - Use generated documents/types from `@/lib/graphql/graphql`.
  - Relay IDs are Global IDs; use `node.id` for list → details navigation.

## Functions, classes, and data
- Favor pure functions; keep side effects explicit.
- Prefer composition over inheritance; use classes only when needed.
- Validate inputs at boundaries and reflect validation in types.

## Async, errors, and resource safety
- Use `async`/`await`; clean up with `try/finally`.
- Never leave floating promises; always `await` or explicitly handle.
- Use typed results for expected failures; reserve `throw` for exceptional cases.

## Collections & immutability
- Prefer immutable updates; mutate only when performance-critical and isolated.
- Use `Map`/`Set` when keys aren’t simple strings.

## Naming & style
- Descriptive identifiers; avoid abbreviations.
- Functions: verb-noun; types/interfaces: noun/adjective.
- Booleans start with `is`/`has`/`should`/`can`.
- Casing: `camelCase` for vars/functions, `PascalCase` for types/classes, `UPPER_SNAKE` for constants.

## Documentation & comments
- Use JSDoc for public APIs (params/returns, units, side effects, throws).
- Comments explain “why,” not “what.”

## Testing & quality
- Prefer deterministic tests; isolate time/randomness via injection.
- Keep snapshots small and intentional.

## Tooling & tsconfig hygiene
- Use Biome for lint/format (`pnpm check`). Avoid ESLint/Prettier.
- Do not change `frontend/tsconfig.json` compiler options unless requested.
- Avoid new path aliases; keep them minimal and documented when necessary.

## Security & robustness
- Validate external data with schema validators and align runtime schema with TS types.
- Avoid stringly-typed APIs; prefer literal unions.
- Sanitize/encode when handling HTML/URLs; avoid unsafe HTML injections.

## Performance
- Measure before optimizing; prefer readability until profiling indicates hotspots.
- Avoid unnecessary allocations in tight loops.

## Generated code guidance
- Prefer small, localized diffs that match repo patterns.
- Always include imports; avoid undeclared globals.
- Do not edit generated code or lockfiles.
- Avoid `// @ts-ignore`; if suppression is unavoidable, use `// @ts-expect-error` with a short reason.
