# GitHub Workflows

## PR Validation

This workflow runs on pull request events (opened, synchronized, reopened, edited).

### PR Jobs

#### Validate PR

- Check PR title follows semantic conventions (`feat`, `fix`, `docs`, etc.)
- Validate PR size is 400 lines of code or less
- Comment on PRs that exceed the size threshold

## CI

This workflow runs automatically on:

- Push to the `main` branch
- Pull requests to the `main` branch

### CI Jobs

#### Verify GraphQL Schema

- Build the GraphQL schema from the backend
- Check that the committed schema is up-to-date

#### Frontend Lint and Test

- Run in a Playwright container
- Use `pnpm` for dependency management with caching
- Install dependencies
- Generate GraphQL code
- Run linting, format checking, type checking, and unit tests

#### Storybook Tests

- Run in a Playwright container (Vitest browser mode)
- Use `pnpm` for dependency management with caching
- Install dependencies
- Generate GraphQL code
- Run Storybook story tests

#### Backend Lint and Test

- Use a PostgreSQL service container
- Install Python dependencies
- Run `ruff` for linting and formatting
- Run `ty` for type checking
- Run `pytest` for tests
