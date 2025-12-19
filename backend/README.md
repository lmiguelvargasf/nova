# Backend

This service runs locally using `uv`.
Docker Compose is used only for the database service.
See the [project root README](../README.md) for setup and running instructions.

## Access Backend

- [Backend Admin UI](http://localhost:8000/admin/)
- [Backend Health Check](http://localhost:8000/health)
- [GraphQL Endpoint (GraphiQL)](http://localhost:8000/graphql)

## Admin UI (SQLAdmin)

The admin UI is backed by SQLAlchemy models and is protected with **session-based login** (email/password) via SQLAdmin's `AuthenticationBackend`.

- **Required env vars**:
  - `ADMIN_SESSION_SECRET`

- **Create the first admin user**:
  - `task backend:create-admin-user`
  - You can also pass env vars to avoid prompts: `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_FIRST_NAME`, `ADMIN_LAST_NAME`

## Migrations (Advanced Alchemy / Alembic)

- **Apply migrations**: `task backend:migrate`
- **Create migrations** (CLI): `uv run litestar database make-migrations --no-prompt -m "your message"`

## Tooling

The following tools are used in this project:

- **[ruff][]:** Used for code linting and formatting.
- **[pytest][]:** Used for running tests.
- **[pytest-cov][]:** Used for measuring test coverage.
- **[pyrefly][]:** Used for static type checking.


## Development Tasks

This project uses [Task][] as a task runner to simplify common development workflows like linting, formatting, and testing.

To see all available tasks and their descriptions, run:

```bash
task --list
```

[Task]: https://taskfile.dev/
[pyrefly]: https://pyrefly.org/
[pytest]: https://docs.pytest.org/
[pytest-cov]: https://pytest-cov.readthedocs.io/en/latest/readme.html
[ruff]: https://docs.astral.sh/ruff/
