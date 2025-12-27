#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
MISE_BIN=""
DB_STARTED=0

info() { printf "\033[1;34m[info]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[warn]\033[0m %s\n" "$*"; }
err() { printf "\033[1;31m[error]\033[0m %s\n" "$*"; }
die() { err "$*"; exit 1; }

have() { command -v "$1" >/dev/null 2>&1; }

stop_db() {
  if [[ "${DB_STARTED}" == "1" && -n "${MISE_BIN:-}" ]]; then
    info "Stopping database..."
    "${MISE_BIN}" exec -- task db:stop || true
    DB_STARTED=0
  fi
}

cleanup() {
  local rc=$?
  stop_db
  exit "$rc"
}

pick_mise() {
  if have mise; then command -v mise; return 0; fi
  if [[ -x "${HOME}/.local/bin/mise" ]]; then echo "${HOME}/.local/bin/mise"; return 0; fi
  return 1
}

ensure_docker_compose() {
  have docker || die "Docker is required. Install Docker Desktop."
  docker compose version >/dev/null 2>&1 || die "'docker compose' is required. Install Docker Desktop."

  if ! docker info >/dev/null 2>&1; then
    die "Docker daemon not running. Please start Docker and re-run ./dev.sh."
  fi
}

install_mise() {
  if pick_mise >/dev/null 2>&1; then return 0; fi

  info "Installing mise via install script..."
  curl https://mise.run | sh

  if ! pick_mise >/dev/null 2>&1; then
    die "mise not found after installation. Check ~/.local/bin/mise or run: curl https://mise.run | sh"
  fi
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

main() {
  cd "$ROOT_DIR"

  ensure_docker_compose
  install_mise

  MISE_BIN="$(pick_mise)"

  info "Using mise: $("${MISE_BIN}" --version | head -n1)"

  trap cleanup EXIT

  info "Installing toolchain..."
  "${MISE_BIN}" install -y

  info "Installing pre-commit hooks..."
  "${MISE_BIN}" exec -- pre-commit install || die "pre-commit install failed. Re-run with: mise exec -- pre-commit install"

  info "Bootstrapping env files..."
  copy_if_missing "${ROOT_DIR}/.env.example" "${ROOT_DIR}/.env"
  copy_if_missing "${ROOT_DIR}/backend/.env.example" "${ROOT_DIR}/backend/.env"
  copy_if_missing "${ROOT_DIR}/frontend/.env.local.example" "${ROOT_DIR}/frontend/.env.local"

  info "Installing backend deps..."
  "${MISE_BIN}" exec -- task backend:install

  info "Installing frontend deps..."
  "${MISE_BIN}" exec -- task frontend:install

  info "Running migrations..."
  DB_STARTED=1
  "${MISE_BIN}" exec -- task backend:migrate

  info "Seeding admin user"
  "${MISE_BIN}" exec -- task backend:create-admin-user -- --email admin@local.dev --password admin

  stop_db

  info "Running codegen..."
  "${MISE_BIN}" exec -- task frontend:codegen

  printf "\n"
  info "Bootstrap complete."
  printf "\n"
  cat <<EOF
Start services in separate terminals:
  task backend:dev
  task frontend:dev

URLs:
  Frontend:  http://localhost:3000
  Backend:   http://localhost:8000/health
  Admin:     http://localhost:8000/admin (admin@local.dev / admin)
  GraphQL:   http://localhost:8000/graphql
EOF
}

main "$@"
