<!-- cursor:
description: GraphQL contract + codegen sync (Strawberry backend ↔ TypeScript frontend)
globs:
  - backend/**/*.py
  - backend/**/*.graphql
  - frontend/**/*.ts
  - frontend/**/*.tsx
  - frontend/**/*.graphql
  - frontend/**/codegen.*
alwaysApply: false
-->

<!-- antigravity:
trigger: always_on
-->

# GraphQL Contract & Sync

## 1) Contract Principles
- **Source of Truth**: The Strawberry backend defines the schema. `frontend/schema/schema.graphql` is the exported SDL version of this truth.
- **No Manual Types**: Never hand-write TypeScript interfaces for GraphQL results. Use types generated in `frontend/src/lib/graphql/`.
- **Atomic Changes**: A schema change and its corresponding frontend sync (codegen + usage fixes) should be in the same change set.

## 2) The Golden Loop (Sync Workflow)
Whenever you modify backend types/resolvers or frontend `.graphql` documents:
1.  **Backend**: Implement changes in `backend/src/backend/apps/**/graphql/`.
2.  **Sync**: Run `task frontend:codegen` from the root. This:
    - Runs `task backend:schema:export` to update the SDL.
    - Runs `pnpm codegen` in the frontend to update generated TS types.
3.  **Frontend**: Fix TS errors in `frontend/src/` using the updated types/fragments.
4.  **Verify**: Run `task frontend:check` to ensure no linting or type regressions.

## 3) Backend Design (Strawberry +  SQLAlchemy [via Advaned Alchemy])
- **Naming**: Use Python `snake_case` for fields; Strawberry automatically converts to `camelCase` for the schema.
- **Nullability**:
  - Be explicit: use `T | None` in Python for nullable fields.
  - Default to nullable for DB relationships unless existence is guaranteed.
- **Performance**: Avoid N+1 by using SQLAlchemy eager-loading patterns (e.g. `selectinload`/`joinedload`) and keeping resolvers thin by moving complex logic to service modules.

## 4) Frontend Practice (Apollo + Client Preset)
- **Colocation**: Keep `.graphql` files (queries/mutations/fragments) next to the components that use them.
- **Fragment Masking**: Use fragments for component data requirements. Import from the generated index:
  ```typescript
  import { graphql } from '@/lib/graphql';
  // Use generated fragment types for props
  import { UserProfileFragment } from '@/lib/graphql/graphql';
  ```
- **Query Minimal**: Only fetch fields required by the UI to reduce payload size.

## 5) Breaking Change Policy
- **Breaking**: Removing/renaming fields, `Nullable -> Non-Null`, or adding required arguments.
- **Safe**: Adding nullable fields, optional arguments, or new types.
- **Protocol**: If a breaking change is required, you **must** update all affected frontend usages immediately after running codegen. Do not leave the frontend in a broken state.

## 6) Relay IDs & List → Details
- **Relay IDs**: Types implementing `strawberry.relay.Node` expose `id` as a Relay Global ID (base64 of `"TypeName:<node_id>"`).
- **Best practice**:
  - Use connection fields (e.g. `users`) for lists and store `node.id`.
  - Use a dedicated GlobalID-based field (e.g. `userById(id: ID!)`) or `node(id: ID!)` to fetch details.
    - Note: Strawberry uses the GraphQL scalar name `ID` for Relay Global IDs.
- **Avoid mixing ID formats**: Keep legacy numeric-ID fields separate from GlobalID fields to prevent ambiguity.
