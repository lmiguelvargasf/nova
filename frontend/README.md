# Frontend

Runs locally using `pnpm`.
See the [project root README](../README.md) for setup instructions.

## Access

- [Application](http://localhost:3000)

## Progressive Web App (PWA)

- Manifest route: [http://localhost:3000/manifest.webmanifest](http://localhost:3000/manifest.webmanifest)
- Service worker: [http://localhost:3000/sw.js](http://localhost:3000/sw.js)
- Current scope includes installable PWA metadata and service worker registration.
- Offline runtime caching and push notifications are not included in this pass.

## Tooling

- **[Biome][]** – Linting and formatting
- **[Vitest][]** – Unit and component tests
- **[Playwright][]** – End-to-end tests
- **[Storybook][]** – UI component development

[Biome]: https://biomejs.dev/
[Playwright]: https://playwright.dev/
[Vitest]: https://vitest.dev/
[Storybook]: https://storybook.js.org/
