# Frontend

This service is containerized via Docker Compose. See the [project root README](../README.md) for setup and running instructions.

## Access Frontend

- [Frontend Application](http://localhost:3000)

## Tooling

The following tools are used in this project:

- **[Biome][]:** Used for code linting and formatting.
- **[Vitest][]:** Used for running unit and component tests.
- **[Playwright][]:** Used for running end-to-end tests.
- **[Storybook][]:** Used for UI component development and testing.

## Development Tasks

This project uses [Task][] as a task runner to simplify common development workflows like linting, formatting, testing, and running the application.

To see all available tasks and their descriptions, run:

```bash
task --list
```

[Biome]: https://biomejs.dev/
[Playwright]: https://playwright.dev/
[Task]: https://taskfile.dev/
[Vitest]: https://vitest.dev/
[Storybook]: https://storybook.js.org/
