#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

info() { printf "\033[1;34m[info]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[warn]\033[0m %s\n" "$*"; }
err() { printf "\033[1;31m[error]\033[0m %s\n" "$*"; }
die() { err "$*"; exit 1; }

have() { command -v "$1" >/dev/null 2>&1; }

pick_mise() {
  if have mise; then command -v mise; return 0; fi
  if [[ -x "${HOME}/.local/bin/mise" ]]; then echo "${HOME}/.local/bin/mise"; return 0; fi
  return 1
}

pick_mprocs() {
  if have mprocs; then command -v mprocs; return 0; fi
  return 1
}

ensure_docker_compose() {
  have docker || die "Docker is required. Install Docker Desktop (macOS) or Docker Engine (Linux)."
  docker compose version >/dev/null 2>&1 || die "'docker compose' is required. Install Docker Desktop (macOS) or the Docker Compose plugin (Linux)."

  if ! docker info >/dev/null 2>&1; then
    die "Docker daemon not running. Please start Docker and re-run ./dev.sh."
  fi
}

install_mise() {
  if pick_mise >/dev/null 2>&1; then return 0; fi

  info "Installing mise via install script..."
  curl -fsSL https://mise.run | sh

  if ! pick_mise >/dev/null 2>&1; then
    die "mise install finished but mise was not found at expected locations (e.g. ~/.local/bin/mise). Verify with: ~/.local/bin/mise --version"
  fi
}

ensure_mprocs_via_mise() {
  local mise_bin="$1"
  if "${mise_bin}" exec -- mprocs --version >/dev/null 2>&1; then
    return 0
  fi
  die "mprocs is required but not available via mise. Try re-running: mise install"
}

copy_if_missing() {
  local src="$1"
  local dst="$2"
  if [[ -f "$dst" ]]; then
    return 0
  fi
  [[ -f "$src" ]] || die "Missing template file: $src"
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  info "Created $(realpath "$dst" 2>/dev/null || echo "$dst")"
}

wait_for_db_healthy() {
  local timeout_s="${1:-120}"
  local start
  start="$(date +%s)"

  local cid=""
  cid="$(docker compose -f "${ROOT_DIR}/compose.yaml" ps -q db 2>/dev/null || true)"
  [[ -n "$cid" ]] || die "Database container not found. Try: docker compose up -d db"

  info "Waiting for Postgres healthcheck..."
  while true; do
    local now
    now="$(date +%s)"
    if (( now - start > timeout_s )); then
      die "Postgres did not become healthy within ${timeout_s}s. Try: docker compose ps && docker logs db"
    fi

    local status=""
    status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$cid" 2>/dev/null || true)"
    if [[ "$status" == "healthy" ]]; then
      info "Postgres is healthy."
      return 0
    fi
    sleep 2
  done
}

main() {
  cd "$ROOT_DIR"

  ensure_docker_compose
  install_mise

  local MISE_BIN
  MISE_BIN="$(pick_mise)"

  info "Using mise: $("${MISE_BIN}" --version | head -n1)"

  info "Installing toolchain (mise)..."
  "${MISE_BIN}" install
  ensure_mprocs_via_mise "${MISE_BIN}"

  info "Installing pre-commit hooks..."
  "${MISE_BIN}" exec -- pre-commit install || die "pre-commit install failed. Re-run with: mise exec -- pre-commit install"

  info "Bootstrapping env files (copy-if-missing)..."
  copy_if_missing "${ROOT_DIR}/.env.example" "${ROOT_DIR}/.env"
  copy_if_missing "${ROOT_DIR}/backend/.env.example" "${ROOT_DIR}/backend/.env"
  copy_if_missing "${ROOT_DIR}/frontend/.env.local.example" "${ROOT_DIR}/frontend/.env.local"

  info "Pulling database image (task db:pull)..."
  "${MISE_BIN}" exec -- task db:pull

  info "Starting database (task db:up)..."
  "${MISE_BIN}" exec -- task db:up
  wait_for_db_healthy 60

  info "Installing backend deps..."
  "${MISE_BIN}" exec -- task -d backend install

  info "Installing frontend deps..."
  "${MISE_BIN}" exec -- task -d frontend install

  info "Running migrations..."
  "${MISE_BIN}" exec -- task -d backend migrate

  info "Seeding admin user (admin@local.dev / admin)..."
  "${MISE_BIN}" exec -- task -d backend create-admin-user -- --email admin@local.dev --password admin

  info "Running codegen..."
  "${MISE_BIN}" exec -- task -d frontend codegen

  printf "\n"
  info "Starting services with mprocs (separate panes/logs)..."
  info "Select the 'info' process to see URLs/credentials."
  printf "\n"

  exec "${MISE_BIN}" exec -- mprocs -c "${ROOT_DIR}/mprocs.yaml"
}

main "$@"
