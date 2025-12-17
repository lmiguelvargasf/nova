# GitHub Workflows

## PR Validation

This workflow runs on pull request events (opened, synchronized, reopened, edited).

### Jobs

#### Validate PR
- Check PR title follows semantic conventions (`feat`, `fix`, `docs`, etc.)
- Validate PR size is 400 lines of code or less
- Comment on PRs that exceed the size threshold

## CI

This workflow runs automatically on:
- Push to the `main` branch
- Pull requests to the `main` branch

### Jobs

#### Generate GraphQL Schema
- Build the GraphQL schema from the backend
- Upload it as an artifact for frontend use

#### Frontend Lint and Test
- Run in a Playwright container
- Use `pnpm` for dependency management with caching
- Install dependencies
- Download the GraphQL schema artifact
- Generate GraphQL code
- Run linting, format checking, and tests

#### Backend Lint and Test
- Use a PostgreSQL service container
- Install Python dependencies
- Run `ruff` for linting and formatting
- Run `pyrefly` for type checking
- Run `pytest` for tests (without coverage)
