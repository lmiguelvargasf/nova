---
applyTo: "backend/**/*, Taskfile.yml, compose.yaml, frontend/schema/schema.graphql"
---

# Backend instructions

## Scope boundary

- Keep all backend logic within `backend/`. Do not import from `frontend/`.
- Cross-repo changes are allowed only when required by the task.
- Contract sync changes include GraphQL schema/codegen outputs (e.g.,
  `task backend:schema:export` / `task frontend:codegen`).
- `.env.example` / README updates when backend env vars or workflows change.

## Technology stack & standards

- Framework: Litestar (`litestar[standard]`). Prefer `async def` handlers for
   IO.
- ORM: SQLAlchemy via Advanced Alchemy (async, Postgres via `asyncpg`).
- GraphQL: Strawberry + `strawberry.litestar` integration.
- Python: `>=3.14` (modern typing; keep type hints accurate for `ty`).
- Settings/validation: `pydantic-settings` (Pydantic v2).
- Package manager: `uv` (`uv.lock` exists). Do not add packages without explicit
   permission.

## Conventions

- Follow existing Litestar conventions and project structure.
- Avoid drive-by refactors; change only what the task requires.

## Code organization

- Keep Strawberry types/queries/mutations/inputs in their module files under
   `backend/src/backend/apps/**/graphql/`.
- Keep resolvers/handlers small and readable. Move multi-step logic into a local
   `services.py` and call it from resolvers/handlers.

## Database & migrations

- Do not manually change DB schema/state outside the migration workflow.
- Any SQLAlchemy model/table change requires a migration and a note on how to
   apply it.
- Prefer Taskfile workflows. If a required workflow is missing
   (e.g., “create a migration”), add a Task target rather than documenting
   multi-step manual commands as the official process.
- If a migration is executed (or the task explicitly asks you to execute it),
  validate reversibility by running `task backend:migrations:migrate` and
  `task backend:migrations:revert`, then re-apply migrations so the local DB
  returns to latest state unless instructed otherwise.

## GraphQL & contracts

- If GraphQL behavior/schema changes, call it out and run the repo’s codegen
   workflow (`task frontend:codegen`) to keep the frontend in sync.

## REST endpoints (Litestar controllers)

- REST endpoints live in `backend/src/backend/apps/**/controllers.py` and should
   use Litestar `Controller` classes.
- Prefer `msgspec.Struct` for request/response bodies (Pydantic only for
   settings).
- Keep handlers thin; move non-trivial logic into `services.py`.
- Pagination (lists):
  - Prefer cursor/keyset pagination over offsets.
  - Use Litestar’s `AbstractAsyncCursorPaginator` and return
    `{ items: [...], page: { next_cursor, limit, has_next } }`.
  - If a filter/sort changes, clients must reset pagination (drop `cursor`).
      Reusing a cursor with different filters should return 400.

## Backend entity definition (when creating a new entity)

### Naming conventions

| Layer            | Pattern             | Example         |
| ---------------- | ------------------- | --------------- |
| Model (ORM)      | `{Entity}Model`     | `UserModel`     |
| Service          | `{Entity}Service`   | `UserService`   |
| GraphQL Type     | `{Entity}Type`      | `UserType`      |
| GraphQL Input    | `{Entity}Input`     | `UserInput`     |
| GraphQL Query    | `{Entity}Query`     | `UserQuery`     |
| GraphQL Mutation | `{Entity}Mutation`  | `UserMutation`  |
| Admin View       | `{Entity}AdminView` | `UserAdminView` |
| Table name       | lowercase singular  | `"user"`        |

### File structure

```text
backend/src/backend/
├── apps/{app_name}/
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy models
│   ├── services.py         # Service + Repository
│   └── graphql/
│       ├── __init__.py     # Exports Query/Mutation classes
│       ├── types.py        # Output types
│       ├── inputs.py       # Input types
│       ├── queries.py      # Query resolvers
│       └── mutations.py    # Mutation resolvers
└── admin/views/
    ├── __init__.py         # ADMIN_VIEWS registry
    └── {entity}.py         # Admin view for entity
```

### Required steps

1. Model (`models.py`)
   - Inherit from `IdentityAuditBase`.
   - Use `Mapped[]` with `mapped_column()`.
   - Set `__tablename__` to lowercase singular.
2. Service (`services.py`)
   - Inherit from `SQLAlchemyAsyncRepositoryService[EntityModel]`.
   - Define nested `Repo` with `model_type`.
3. GraphQL type (`graphql/types.py`)
   - Use `@strawberry.type` + `@dataclass`.
   - Implement `from_model()` for ORM → GraphQL conversion.
   - Implement `relay.Node` and type `id` as `relay.NodeID[int]`.
4. GraphQL input (`graphql/inputs.py`)
   - Use `@strawberry.input` + `@dataclass`.
   - Include only fields needed for creation/mutation.
5. GraphQL query (`graphql/queries.py`)
   - Prefer `*_by_id(id: strawberry.relay.GlobalID)` for details lookup.
   - Prefer Relay connections for lists when appropriate.
6. REST list pagination (when adding REST list endpoints)
   - Use cursor pagination with `limit` + optional `cursor` and the
     `{ items, page }` response envelope.
7. GraphQL mutation (`graphql/mutations.py`)
   - Use `@strawberry.type` + `@strawberry.mutation`.
   - Handle `DuplicateKeyError` and `RepositoryError` → `GraphQLError`.
   - Call `db_session.rollback()` on errors; use `auto_commit=True` for
     single-operation mutations.
8. GraphQL exports (`graphql/__init__.py`)
   - Export Query/Mutation classes.
9. Schema registration (`backend/src/backend/schema.py`)
   - Add the new Query/Mutation via inheritance in the root schema.
10. Service registration (context): ensure the service is available in GraphQL
   context via dependency injection/context factory.
11. Admin view (`backend/src/backend/admin/views/{entity}.py`): inherit from
   `ModelView`, set label/name/identity, and export `view`.
12. Admin registration (`backend/src/backend/admin/views/__init__.py`): add the
   new view to `ADMIN_VIEWS`.
13. Migration: generate and apply a migration using Taskfile targets (review
   the generated file). If migrations are run, verify downgrade works by
   reverting the latest migration and migrating again.

## Validation workflow

Before declaring a backend task complete:

- Run `task backend:format`, `task backend:lint`, `task backend:typecheck`,
  `task backend:test`.
- If GraphQL was touched: run `task frontend:codegen` and ensure
   `frontend/schema/schema.graphql` updates accordingly.
