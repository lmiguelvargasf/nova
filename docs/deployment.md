## Production Deployment

This template has been verified running in production with:
- **Database**: [Render][render] Postgres
- **Backend**: [Render][render]
- **Frontend**: [Vercel][vercel]

## Database (Render)

Create a **Render Postgres** instance.

## Backend (Render)

Deploy the backend as a **Render Web Service**.

- **Root Directory**: `backend`
- **Build Command**: `uv sync`
- **Environment Variables**: add all variables defined in `.env.example` and `backend/.env.example` to your Render service settings.

### Render commands

#### Free plan

- **Start Command**:
  - `uv run litestar database upgrade --no-prompt && uv run uvicorn backend:app --host 0.0.0.0 --port $PORT`

#### Starter plan (recommended for cleaner deploy separation)

- **Pre-Deploy Command**:
  - `uv run litestar database upgrade --no-prompt`
- **Start Command**:
  - `uv run uvicorn backend:app --host 0.0.0.0 --port $PORT`

## Frontend (Vercel)

Deploy the frontend as a **Vercel Project**.

- **Root Directory**: `frontend`
- **Environment Variables**: add all variables defined in `frontend/.env.local.example` to your Vercel project settings.

[render]: https://render.com/
[vercel]: https://vercel.com/
