# Nova 🌟

![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.14-blue?style=for-the-badge&logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?style=for-the-badge&logo=typescript)
![Node.js](https://img.shields.io/badge/node.js-24-brightgreen?style=for-the-badge&logo=node.js)
![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-0074D9?style=for-the-badge&logo=postgresql&logoColor=white)
![GraphQL](https://img.shields.io/badge/GraphQL-E10098?style=for-the-badge&logo=graphql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-0074D9?style=for-the-badge&logo=docker&logoColor=white)
![Task](https://img.shields.io/badge/Task-43B883?style=for-the-badge&logo=task&logoColor=white)

A full-stack application template with a Python (Litestar) backend and a TypeScript (Next.js) frontend, connected via GraphQL. Ideal for quickly bootstrapping proof-of-concept (PoC) projects.

## 📚 Table of Contents

- [Tech Stack](#️-tech-stack)
- [Getting Started](#-getting-started)
- [Production Deployment](#-production-deployment-supabase--render--vercel)
- [Development Tasks](#️-development-tasks)
- [CI/CD Workflows](#-cicd-workflows)
- [Releases](#-releases)
- [License](#-license)

## 🛠️ Tech Stack

### Backend
- **[Python][python]** – Core programming language for backend.
- **[Litestar][litestar]** – High-performance ASGI framework for modern Python web apps.
- **[Advanced Alchemy][advanced-alchemy]** – SQLAlchemy integration (async) + migrations tooling.
- **[PostgreSQL][postgresql]** – Advanced open-source relational database known for reliability.
- **[GraphQL][graphql]** – API query language providing a more efficient alternative to REST.

### Frontend
- **[TypeScript][typescript]** – Core programming language for frontend.
- **[Next.js][nextjs]** – React framework for production-ready applications.
- **[Tailwind CSS][tailwind]** – Utility-first CSS framework for rapid UI development.

## 🚀 Getting Started

### Prerequisites

- **[Docker Desktop][docker-desktop]**: Provides Docker Engine and Docker Compose.
- **[mise][mise]**: Manages tools like `uv`, `pnpm`, and `task`.

### Environment Setup

1. Install the project toolchain:
   ```bash
   mise install
   ```

1. Copy the example environment files:
   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
   ```

1. Edit the environment files (`.env`, `backend/.env`, and `frontend/.env.local`) to set the required secrets and configuration values (such as database URLs, API keys, etc.).

1. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Starting the Application

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

1. Generate frontend code based on the backend API:
   ```bash
   task frontend:codegen
   ```
   **Note:** This exports the GraphQL schema from the backend into `frontend/schema/schema.graphql` and then runs code generation.

1. Start frontend:
   ```bash
   task frontend:dev
   ```

1. Create an initial admin user:
   ```bash
   task backend:create-admin-user
   ```

The services will be available at:
- [Frontend Application](http://localhost:3000)
- [Backend Health Check](http://localhost:8000/health)
- [Admin UI](http://localhost:8000/admin)
- [GraphQL Endpoint (GraphiQL)](http://localhost:8000/graphql)

## 🌐 Production Deployment (Supabase + Render + Vercel)

This is an opinionated deployment recommendation that has worked well in production, but you are free to deploy this template using any providers or infrastructure that fit your needs.

See full deployment details in [`docs/deployment.md`](docs/deployment.md).

## ⚙️ Development Tasks

This project uses [Task][] to simplify common development workflows. The main `Taskfile.yml` in the project root provides commands for:

- Managing the Docker environment (for example, building, starting, or stopping services).
- Running development tasks within the `backend` and `frontend` services (such as linting, formatting, or testing).

To list all available tasks, run:

```bash
task --list
```

## 🔄 CI/CD Workflows

This project uses GitHub Actions for continuous integration and validation:

- **PR Validation**: Enforce PR title conventions and limit PR size.
- **CI Workflow**: Run tests and linting on both frontend and backend.

For detailed information about our CI/CD workflows, see the [workflows documentation](.github/workflows/README.md).

## 📦 Releases

All versioned changes are documented on the [GitHub Releases][releases] page.

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

[advanced-alchemy]: https://docs.advanced-alchemy.litestar.dev/
[docker-desktop]: https://www.docker.com/products/docker-desktop/
[graphql]: https://graphql.org/
[litestar]: https://litestar.dev/
[mise]: https://mise.jdx.dev/
[nextjs]: https://nextjs.org/
[postgresql]: https://www.postgresql.org/
[pre-commit]: https://pre-commit.com/
[python]: https://www.python.org/
[releases]: https://github.com/lmiguelvargasf/nova/releases
[tailwind]: https://tailwindcss.com/
[task]: https://taskfile.dev/
[typescript]: https://www.typescriptlang.org/
