# Backend

Runs locally using `uv`. Docker Compose is used only for the database.
See the [project root README](../README.md) for setup instructions.

## Access

- [Health Check](http://localhost:8000/health)
- [Admin UI](http://localhost:8000/admin)
- [GraphQL (GraphiQL)](http://localhost:8000/graphql)

## Tooling

- **[Advanced Alchemy][]** – ORM and database migrations
- **[ruff][]** – Linting and formatting
- **[pytest][]** – Testing
- **[pytest-cov][]** – Test coverage
- **[ty][]** – Static type checking

[Advanced Alchemy]: https://docs.advanced-alchemy.litestar.dev/latest/
[pytest]: https://docs.pytest.org/
[pytest-cov]: https://pytest-cov.readthedocs.io/en/latest/readme.html
[ruff]: https://docs.astral.sh/ruff/
[ty]: https://docs.astral.sh/ty/
