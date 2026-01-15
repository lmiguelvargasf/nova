# Nova 🌟

![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.14-blue?style=for-the-badge&logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?style=for-the-badge&logo=typescript)
![Node.js](https://img.shields.io/badge/node.js-24-brightgreen?style=for-the-badge&logo=node.js)
![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-0074D9?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.6-37814A?style=for-the-badge&logo=celery&logoColor=white)
![GraphQL](https://img.shields.io/badge/GraphQL-E10098?style=for-the-badge&logo=graphql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-0074D9?style=for-the-badge&logo=docker&logoColor=white)
![Task](https://img.shields.io/badge/Task-43B883?style=for-the-badge&logo=task&logoColor=white)

A full-stack application template with a Python (Litestar) backend and a
TypeScript (Next.js) frontend, connected via GraphQL and REST. Ideal for
hackathons and rapid prototyping, designed to smoothly evolve from a PoC into
an MVP.

## 📚 Table of Contents

- [Nova 🌟](#nova-)
  - [📚 Table of Contents](#-table-of-contents)
  - [🛠️ Tech Stack](#️-tech-stack)
    - [Backend](#backend)
    - [Frontend](#frontend)
    - [Tooling](#tooling)
  - [🚀 Getting Started](#-getting-started)
    - [Prerequisites](#prerequisites)
    - [Scripted setup (recommended)](#scripted-setup-recommended)
    - [Step-by-step setup (manual)](#step-by-step-setup-manual)
      - [Local environment](#local-environment)
      - [Start services](#start-services)
  - [💻 Developer Experience](#-developer-experience)
  - [📏 Rules System](#-rules-system)
  - [🌐 Production Deployment](#-production-deployment)
  - [⚙️ Development Tasks](#️-development-tasks)
  - [🔄 CI/CD Workflows](#-cicd-workflows)
  - [📦 Releases](#-releases)
  - [📄 License](#-license)

## 🛠️ Tech Stack

### Backend

- **[Python][]** – Core programming language for backend.
- **[Litestar][]** – High-performance ASGI framework for modern Python web apps.
- **[Advanced Alchemy][]** – SQLAlchemy integration (async) + migrations tooling.
- **[GraphQL][]** – API query language for flexible data fetching.
- **[REST][]** – Resource-oriented APIs over HTTP with JSON.
- **[PostgreSQL][]** – Advanced open-source relational database known for reliability.
- **[Redis][]** – In-memory data store for message brokering.
- **[Celery][]** – Distributed task queue for handling asynchronous background jobs.
- **[Flower][]** – Real-time monitoring for Celery workers.
- **[uv][]** – Ultra-fast Python package and project manager.
- **[ruff][]** – Extremely fast Python linter and code formatter.
- **[ty][]** – Fast, type-safe Python type checker.

### Frontend

- **[TypeScript][]** – Core programming language for frontend.
- **[Next.js][]** – React framework for production-ready applications.
- **[Tailwind CSS][]** – Utility-first CSS framework for rapid UI development.
- **[pnpm][]** – Fast, disk space efficient package manager.
- **[Storybook][]** – Tool for building UI components and pages in isolation.
- **[Vitest][]** – Next generation testing framework.
- **[Playwright][]** – Reliable end-to-end testing for modern web apps.
- **[Biome][]** – Fast formatter and linter for JavaScript/TypeScript projects.

### Tooling

- **[Docker Desktop][]** – Provides Docker Engine and Docker Compose.
- **[mise][]** – Manages tool versions.
- **[Task][]** – Task runner designed for modern workflows.
- **[pre-commit][]** – Manages and runs automated Git hooks.

## 🚀 Getting Started

### Prerequisites

- **[Docker Desktop][]**

### Scripted setup (recommended)

Run the setup script to install dependencies and configure the environment:

```bash
./setup.sh
```

> **Note:** if you get _permission denied_, run `chmod +x setup.sh` then retry
> `./setup.sh`.

After it finishes, start services in separate terminals:

```bash
task backend:dev
task frontend:dev
```

### Step-by-step setup (manual)

#### Local environment

1. Verify Docker is available:

    ```bash
    docker --version
    docker compose version
    docker info
    ```

1. Install mise:

    ```bash
    curl https://mise.run | sh
    ```

    If this fails, see the official [install docs][mise-install].

1. Install the project toolchain:

    ```bash
    mise install -y
    ```

1. Install pre-commit hooks:

    ```bash
    pre-commit install
    ```

1. Copy the example environment files:

    ```bash
    cp .env.example .env
    cp backend/.env.example backend/.env
    cp frontend/.env.local.example frontend/.env.local
    ```

#### Start services

1. Pull database image:

    ```bash
    task db:pull
    ```

1. Start database service:

    ```bash
    task db:up
    ```

1. Install backend dependencies:

    ```bash
    task backend:install
    ```

1. Install frontend dependencies:

    ```bash
    task frontend:install
    ```

1. Start backend:

    ```bash
    task backend:dev
    ```

1. Create an initial admin user:

    ```bash
    task backend:create-admin-user
    ```

1. Generate frontend code based on the backend API:

    ```bash
    task frontend:codegen
    ```

1. Start frontend:

    ```bash
    task frontend:dev
    ```

1. Start background worker:

    ```bash
    task worker:dev
    ```

1. Start periodic task scheduler:

    ```bash
    task beat:dev
    ```

1. Start monitoring (optional):

    ```bash
    task flower:up
    ```

The services will be available at:

- [Frontend Application](http://localhost:3000)
- [Backend Health Check](http://localhost:8000/health)
- [Admin UI](http://localhost:8000/admin)
- [GraphQL Endpoint (GraphiQL)](http://localhost:8000/graphql)
- [Flower Monitoring](http://localhost:5555)

## 💻 Developer Experience

This project is pre-configured for **VS Code** (or any fork like **Cursor** or
**Windsurf**) to provide a seamless development experience:

- **Type Checking**: Since we use `ty`, the `"python.languageServer"` setting is
    set to `"None"` in [`.vscode/settings.json`](.vscode/settings.json). This
    avoids running two language servers simultaneously when the Python extension
    is enabled (see [official ty configuration][ty-editors]).

## 📏 Rules System

This project uses a canonical rule system to manage AI/LLM coding rules (for
Cursor, Antigravity, etc.).

- Rules are defined in `.rules/*.md`.
- Tool-specific configurations are generated automatically.
- See full documentation in [`docs/rules.md`](docs/rules.md).

## 🌐 Production Deployment

This is an opinionated deployment recommendation that has worked well in
production, but you are free to deploy this template using any providers or
infrastructure that fit your needs.

This template has been deployed successfully with the **frontend on Vercel** and
the **backend + database on Render**.

See full deployment details in [`docs/deployment.md`](docs/deployment.md).

## ⚙️ Development Tasks

This project uses [Task][] to simplify common development workflows. The main
`Taskfile.yml` in the project root provides commands for:

- Managing the Docker environment (for example, building, starting, or stopping
    services).
- Running development tasks within the `backend` and `frontend` services (such
    as linting, formatting, or testing).
- Managing background workers (Celery worker and beat).

To list all available tasks, run:

```bash
task --list
```

## 🔄 CI/CD Workflows

This project uses GitHub Actions for continuous integration and validation:

- **PR Validation**: Enforce PR title conventions and limit PR size.
- **CI Workflow**: Run tests and linting on both frontend and backend.

For detailed information about our CI/CD workflows, see the
[workflows documentation](.github/workflows/README.md).

## 📦 Releases

All versioned changes are documented on the [GitHub Releases][releases] page.

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

[advanced alchemy]: https://docs.advanced-alchemy.litestar.dev/
[biome]: https://biomejs.dev/
[celery]: https://docs.celeryq.dev/
[docker desktop]: https://www.docker.com/products/docker-desktop/
[flower]: https://flower.readthedocs.io/
[graphql]: https://graphql.org/
[litestar]: https://litestar.dev/
[mise]: https://mise.jdx.dev/
[mise-install]: https://mise.jdx.dev/getting-started.html
[next.js]: https://nextjs.org/
[playwright]: https://playwright.dev/
[pnpm]: https://pnpm.io/
[postgresql]: https://www.postgresql.org/
[pre-commit]: https://pre-commit.com/
[python]: https://www.python.org/
[redis]: https://redis.io/
[releases]: https://github.com/lmiguelvargasf/nova/releases
[rest]: https://restfulapi.net/
[ruff]: https://docs.astral.sh/ruff/
[storybook]: https://storybook.js.org/
[tailwind css]: https://tailwindcss.com/
[task]: https://taskfile.dev/
[ty]: https://docs.astral.sh/ty/
[ty-editors]: https://docs.astral.sh/ty/editors/
[typescript]: https://www.typescriptlang.org/
[uv]: https://docs.astral.sh/uv/
[vitest]: https://vitest.dev/
