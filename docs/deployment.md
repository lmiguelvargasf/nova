## Production Deployment (Supabase + Render + Vercel)

This template has been verified running in production with:
- **Database**: [Supabase][supabase] Postgres
- **Backend**: [Render][render]
- **Frontend**: [Vercel][vercel]

## Database (Supabase)

- **Important**: use the **Session Pooler** connection string (Render connects via IPv4).

## Backend (Render)

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

- **Root Directory**: `frontend`
- **Environment Variables**: add all variables defined in `frontend/.env.local.example` to your Vercel project settings.

[render]: https://render.com/
[supabase]: https://supabase.com/
[vercel]: https://vercel.com/
