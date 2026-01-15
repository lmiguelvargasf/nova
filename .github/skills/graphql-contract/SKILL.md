---
name: graphql-contract
description: Use when changing GraphQL schema, resolvers, or frontend GraphQL documents so the contract and codegen stay in sync.
---

# GraphQL contract & sync

## When to use

- You modify backend GraphQL types/resolvers or the schema.
- You add or edit frontend `.graphql` documents.
- You suspect schema and generated types are out of sync.

## Steps

1. Backend: implement changes under `backend/src/backend/apps/**/graphql/`.
2. Sync: run `task frontend:codegen` from the repo root.
   - This runs `task backend:schema:export` to update `frontend/schema/schema.graphql`.
   - Then runs `pnpm codegen` to regenerate TypeScript types.
3. Frontend: update `frontend/src/` to use the newly generated types/fragments.
4. Verify: run `task frontend:check`.

## Constraints and guardrails

- The Strawberry backend is the source of truth; do not manually edit `frontend/schema/schema.graphql`.
- Do not hand-write TypeScript interfaces for GraphQL results; use generated types in `frontend/src/lib/graphql/`.
- Schema changes and frontend sync should be in the same change set.
- Breaking changes (removing/renaming fields, `Nullable → Non-Null`, adding required args) require immediate frontend updates after codegen.
- Avoid N+1 by using SQLAlchemy eager loading (`selectinload`/`joinedload`) and moving complex logic into services.

## References

- `backend/src/backend/apps/**/graphql/`
- `frontend/schema/schema.graphql`
- `frontend/src/lib/graphql/`
- `frontend/**/codegen.*`
