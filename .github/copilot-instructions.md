# AI Coding Agent Instructions

## Project Overview

**Nova** is a full-stack application template with:
- **Backend**: Python 3.14 + Litestar (ASGI framework) + PostgreSQL + Redis
- **Frontend**: TypeScript + Next.js 16 + React 19
- **API Layer**: GraphQL (primary) + REST endpoints
- **Async Tasks**: Celery 5.6 workers + Celery Beat scheduler
- **Dev Tools**: Task runner, mise (version manager), Docker Compose, uv (Python package manager)

## Architecture Patterns

### Backend Structure (Apps-Based Design)

The backend uses a **domain-driven modular architecture**. Each domain lives in `backend/src/backend/apps/<domain>/`:
- `models.py` – SQLAlchemy ORM models with async support via Advanced Alchemy
- `services.py` – Business logic (queries, mutations, validations)
- `schemas.py` – Pydantic schemas for REST/validation
- `controllers.py` – Litestar HTTP handlers
- `graphql.py` – Strawberry GraphQL resolvers (Query/Mutation types)
- `auth.py` – Domain-specific authentication/permissions
- `tasks.py` – Celery async tasks

**Example**: `apps/users/` contains user registration, authentication, and profile management—all bundled together.

### Database & ORM

- **Advanced Alchemy** wraps SQLAlchemy with async-first ergonomics
- Models use declarative base with type-safe `Mapped[]` syntax
- **Mixins** (e.g., `SoftDeleteMixin`) provide reusable model behaviors
- All timestamps must use `DateTimeUTC(timezone=True)` for UTC awareness
- Migrations auto-generated via Alembic: `task backend:migrate:make -- "description"`

### API Duality: GraphQL + REST

- **GraphQL** is primary; use Strawberry for schema definition
- **REST** endpoints for simple CRUD exposed via Litestar controllers
- Frontend can toggle between both via `useDataSource()` hook (stored in localStorage)
- GraphQL depth limited to 10 queries by default (`settings.graphql_max_depth`)

### Authentication & Authorization

- JWT tokens via `jwt_auth` (see [backend/src/backend/auth/jwt.py](backend/src/backend/auth/jwt.py))
- User retrieved in `retrieve_user_handler` by token `sub` claim
- Public routes (auth, health, GraphQL, admin) excluded from JWT protection
- Permissions checked in resolvers via `context.user` and `context.services`

### Async Tasks with Celery

- **Workers**: Long-running background jobs, started with `task worker:dev`
- **Beat Scheduler**: Cron jobs defined in `app.conf.beat_schedule` (e.g., daily inactive user deactivation)
- **Task Session Management**: Use `get_task_session()` context manager for async DB access
- **Worker Process Lifecycle**: Engine initialized on `worker_process_init`, disposed on shutdown
- Retry logic: `autoretry_for`, `retry_backoff`, `retry_jitter`, `max_retries`

## Critical Developer Workflows

### Local Development

1. **Setup** (one-time):
   ```bash
   ./setup.sh  # Installs mise, Node/Python toolchains, dependencies, Git hooks
   ```

2. **Start Services** (in separate terminals):
   ```bash
   task backend:dev      # Python dev server + migrations
   task frontend:dev     # Next.js dev server
   task worker:dev       # Celery worker (async jobs)
   task beat:dev         # Celery Beat (scheduler)
   ```
   Or run all at once: `task dev`

3. **Infrastructure** (Docker):
   ```bash
   task infra:up         # Start PostgreSQL + Redis
   task infra:down       # Stop services
   task infra:down:volumes  # Full cleanup
   ```

### Testing

**Backend** (pytest):
```bash
cd backend && task test           # Run all tests
cd backend && task test:watch     # Watch mode
```

**Frontend** (Vitest + Playwright):
```bash
cd frontend && pnpm test:unit       # Unit tests
cd frontend && pnpm test:e2e        # E2E tests
cd frontend && pnpm test:story:run  # Storybook story tests
```

**Validation** (Frontend):
```bash
cd frontend && pnpm validate  # Check + types + tests + build
```

### Database Migrations

```bash
task backend:migrate:make -- "add_user_email_index"  # Auto-generates from model changes
task backend:migrate                                  # Apply pending migrations
```

### Code Quality

**Backend**:
```bash
task backend:check    # Ruff format + lint (fixes most issues)
task backend:lint     # Linter only
task backend:format   # Formatter only
```

**Frontend**:
```bash
cd frontend && pnpm check         # Biome lint + format
cd frontend && pnpm check:types   # TypeScript check
cd frontend && pnpm check:unsafe  # Apply all fixes (including unsafe)
```

## Project-Specific Conventions

### Backend Naming

- Models: `<Domain>Model` (e.g., `UserModel`)
- Services: `<Domain>Service` (e.g., `UserService`)
- GraphQL types: `<Domain>Type` (e.g., `UserType`)
- Controllers: `<Domain>Controller` (e.g., `UserController`)
- Celery tasks: `snake_case_function` with `@app.task` decorator

### Frontend File Organization

- **App Router**: [src/app](frontend/src/app) – layouts, pages, route segments
- **Features**: [src/features](frontend/src/features) – business logic (auth, users)
  - Each feature has `*.client.tsx` (Client Components) and `*.server.tsx` (Server Components)
- **Components**: [src/components/ui](frontend/src/components/ui) – reusable UI (buttons, forms, cards)
- **Libraries**: [src/lib](frontend/src/lib) – utilities, Apollo client, GraphQL codegen output

### Config & Environment

- **Backend**: `backend/.env` + `backend/src/backend/config/base.py` (Pydantic Settings)
- **Frontend**: `frontend/.env.local`
- Root `.env` shared for Docker Compose (DB credentials, Redis, CORS origins)
- All secrets loaded via Pydantic `BaseSettings` (strict validation)

### Version Management

- **Node**: 24.12.0
- **Python**: 3.14
- **TypeScript**: 5.9
- Versions locked in `mise.toml` (tools) + `backend/pyproject.toml` (Python) + `frontend/package.json` (Node)

## Integration Points & External Dependencies

### Frontend-Backend Communication

1. **GraphQL (Primary)**
   - Schema defined in `backend/src/backend/graphql/schema.py`
   - Codegen: `cd frontend && pnpm codegen` generates TypeScript hooks from `schema/schema.graphql`
   - Apollo Client configured in [frontend/src/lib/apollo](frontend/src/lib/apollo)

2. **REST API**
   - Health check: `GET /health` (no auth)
   - User endpoints: `POST /api/auth/login`, `POST /api/auth/register` (Litestar controllers)

3. **Data Source Toggle**
   - Frontend: `useDataSource()` hook switches between GraphQL and REST
   - Stored in localStorage; dispatches custom events for cross-tab sync

### Docker Compose Services

- **PostgreSQL 17**: Port 5432, initialized with `db/init.sql`, health check ensures readiness
- **Redis 7**: Port 6379, used as Celery broker + result backend
- Both optional but required for `task backend:dev` and async tasks

### External Tools

- **Starlette Admin**: Admin panel auto-generated from models (accessible at `/admin`)
- **Flower**: Celery monitoring UI (started with `task beat:dev`)
- **Storybook**: Component library (`pnpm storybook`), integrated with vitest for story testing
- **Playwright**: E2E testing framework with headed/UI modes

## Common Pitfalls & Best Practices

1. **Async/Await in Backend**: Always use `asyncio.run()` in Celery tasks; don't mix sync/async without care
2. **Database Migrations**: After model changes, generate migrations; don't manually edit `versions/` files
3. **Soft Deletes**: Use `SoftDeleteMixin` for user data; queries automatically exclude deleted records
4. **GraphQL Depth Limits**: Keep nested queries shallow; enforce via `QueryDepthLimiter` (default 10)
5. **Frontend SSR**: Use Server Components (`*.server.tsx`) for data fetching; Client Components only for interactivity
6. **Testing DB**: Separate test database (`<DB>_test`) prevents accidents; conftest validates this
7. **Task Idempotency**: Celery tasks may retry; ensure `deactivate_inactive_users` and similar can safely re-run
8. **JWT Excluded Routes**: Changes to excluded routes in [backend/src/backend/auth/jwt.py](backend/src/backend/auth/jwt.py#L17-L23) affect all endpoints

## Key Files Reference

- [backend/src/backend/application.py](backend/src/backend/application.py) – App factory, route registration
- [backend/src/backend/config/base.py](backend/src/backend/config/base.py) – Settings schema
- [backend/src/backend/graphql/schema.py](backend/src/backend/graphql/schema.py) – GraphQL root Query/Mutation
- [backend/celery_app.py](backend/src/backend/celery_app.py) – Celery config, beat schedule
- [frontend/src/app/page.tsx](frontend/src/app/page.tsx) – Home page (landing)
- [frontend/next.config.ts](frontend/next.config.ts) – Next.js build config
- [Taskfile.yml](Taskfile.yml) – Root task definitions
- [compose.yaml](compose.yaml) – Docker Compose services
