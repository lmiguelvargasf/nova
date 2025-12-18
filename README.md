# Nova 🌟

![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.13-blue?style=for-the-badge&logo=python)
![Node.js](https://img.shields.io/badge/node.js-22.14-brightgreen?style=for-the-badge&logo=node.js)
![Next.js](https://img.shields.io/badge/Next.js-15.x-black?style=for-the-badge&logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=for-the-badge&logo=typescript)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-0074D9?style=for-the-badge&logo=postgresql&logoColor=white)
![GraphQL](https://img.shields.io/badge/GraphQL-E10098?style=for-the-badge&logo=graphql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-0074D9?style=for-the-badge&logo=docker&logoColor=white)
![Task](https://img.shields.io/badge/Task-43B883?style=for-the-badge&logo=task&logoColor=white)

A modern full-stack application template built for quick and efficient project setup.

## 📚 Table of Contents

- [Tech Stack](#️-tech-stack)
- [Getting Started](#-getting-started)
- [Development Tasks](#️-development-tasks)
- [Troubleshooting](#-troubleshooting)
- [CI/CD Workflows](#-cicd-workflows)
- [Releases](#-releases)
- [License](#-license)

## 🛠️ Tech Stack

### Backend
- **[Python][python]** – Core programming language for backend.
- **[Litestar][litestar]** – High-performance ASGI framework for modern Python web apps.
- **[Piccolo][piccolo]** – Async ORM and query builder with migration support.
- **[PostgreSQL][postgresql]** – Advanced open-source relational database known for reliability.
- **[GraphQL][graphql]** – API query language providing a more efficient alternative to REST.

### Frontend
- **[TypeScript][typescript]** – Core language for frontend, adding static types to JavaScript.
- **[Next.js][nextjs]** – React framework for production-ready applications.
- **[Tailwind CSS][tailwind]** – Utility-first CSS framework for rapid UI development.
- **[Chart.js][chartjs]** – Simple yet flexible JavaScript charting library.

## 🚀 Getting Started

### Prerequisites

The primary prerequisites for this project are:
- **[Docker Desktop][docker-desktop]:** Provides Docker Engine and Docker Compose.
- **[Task][task]:** A task runner / build tool used for managing common development workflows.
- **[pre-commit][]:** A tool for managing and running pre-commit hooks.
- **[uv][]:** backend package manager.
- **[nvm][]:** Manages your local Node.js versions.
- **[pnpm][]:** frontend package manager.

#### Alternative Installation

Alternatively, install the components separately:
- [**Docker Engine:**](https://docs.docker.com/engine/install/) Version 28 or later.
- [**Docker Compose:**](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually) Version 2 (V2) or later.

#### Verifying Installation

Verify the installation by running:
```bash
docker --version
docker compose version
task --version
pre-commit --version
uv --version
nvm --version
node --version
pnpm --version
```

### Environment Setup

1. Copy the example environment files:
   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
   ```

2. Edit the environment files (`.env`, `backend/.env`, and `frontend/.env.local`) to set the required secrets and configuration values (such as database URLs, API keys, etc.).

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Starting the Application

1. Build the Docker images:
   ```bash
   task docker:build
   ```

2. Start the database service:
   ```bash
   task docker:up
   ```

3. Install backend dependencies:
   ```bash
   task backend:install
   ```

4. Run backend:
   ```bash
   task backend:dev
   ```

5. Install frontend dependencies:
   ```bash
   task frontend:install
   ```

6. Generate frontend code based on the backend API:
   ```bash
   task frontend:codegen
   ```
   **Note:** This exports the GraphQL schema from the backend into `frontend/schema/schema.graphql` and then runs code generation.

7. Start the frontend:
   ```bash
   task frontend:dev
   ```

8. Create an initial admin user:
   ```bash
   task backend:create-user
   ```
   **Note:** *Follow the prompts. Use your email address as the username. You can leave the email field blank when prompted later.*

9. The services will be available at:
   - [Frontend Application](http://localhost:3000)
   - [Backend Admin UI](http://localhost:8000/admin/)
   - [Backend Health Check](http://localhost:8000/health)
   - [GraphQL Endpoint (GraphiQL)](http://localhost:8000/graphql)

10. To stop and remove database service:
   ```bash
   task docker:down
   ```

## ⚙️ Development Tasks

This project uses [Task][] to simplify common development workflows. The main `Taskfile.yml` in the project root provides commands for:

- Managing the Docker environment (for example, building, starting, or stopping services).
- Running development tasks within the `backend` and `frontend` services (such as linting, formatting, or testing).

To list all available tasks, run:

```bash
task --list
```

Refer to the `README.md` files in the [`backend`](./backend/README.md) and [`frontend`](./frontend/README.md) directories for service-specific task details.

## 🧰 Troubleshooting

### Frontend

If GraphQL codegen fails (or your generated types feel out of date):

1. Regenerate the schema + frontend GraphQL types:
   ```bash
   task frontend:codegen
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

[chartjs]: https://www.chartjs.org/
[docker-desktop]: https://www.docker.com/products/docker-desktop/
[graphql]: https://graphql.org/
[litestar]: https://litestar.dev/
[nextjs]: https://nextjs.org/
[nvm]: https://github.com/nvm-sh/nvm
[piccolo]: https://piccolo-orm.com/
[pnpm]: https://pnpm.io/
[postgresql]: https://www.postgresql.org/
[pre-commit]: https://pre-commit.com/
[python]: https://www.python.org/
[releases]: https://github.com/lmiguelvargasf/nova-stack/releases
[tailwind]: https://tailwindcss.com/
[task]: https://taskfile.dev/
[typescript]: https://www.typescriptlang.org/
[uv]: https://docs.astral.sh/uv/
