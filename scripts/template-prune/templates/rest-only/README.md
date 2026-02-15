# Nova REST API Template

A minimal backend-first template using:

- Python 3.14
- Litestar (REST)
- PostgreSQL
- Advanced Alchemy
- Ruff + Ty + Pytest

This pruned profile intentionally removes:

- GraphQL
- Frontend (Next.js)
- iOS template
- Celery/Beat/Flower
- Redis

## Quick start

```bash
./setup.sh
```

Start backend:

```bash
task backend:dev
```

## URLs

- Backend Health: [http://localhost:8000/health](http://localhost:8000/health)
- Admin: [http://localhost:8000/admin](http://localhost:8000/admin)

## Core tasks

- `task backend:install`
- `task backend:migrate`
- `task backend:dev`
- `task backend:test`
- `task backend:check`
- `task backend:typecheck`

## Template prune tasks

- `task template:prune:no-rest`
- `task template:prune:no-graphql`
- `task template:prune:no-ios`
- `task template:prune:rest-only`
- `task template:prune:status`
- `task template:prune:validate -- <profile>`
