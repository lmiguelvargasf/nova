# Backend

This service is containerized via Docker Compose. See the [project root README](../README.md) for setup and running instructions.

## Access Backend

- [Backend Admin UI](http://localhost:8000/admin/)
- [Backend Health Check](http://localhost:8000/health)
- [GraphQL Endpoint (GraphiQL)](http://localhost:8000/graphql)

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

[pyrefly]: https://pyrefly.org/
[pytest]: https://docs.pytest.org/
[pytest-cov]: https://pytest-cov.readthedocs.io/en/latest/readme.html
[ruff]: https://docs.astral.sh/ruff/
[Task]: https://taskfile.dev/
