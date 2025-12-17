FROM ghcr.io/astral-sh/uv:python3.13-bookworm

# Install Taskfile
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d
ENV PATH="${PATH}:/app/bin"

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

CMD ["sh", "/app/entrypoint.sh"]
