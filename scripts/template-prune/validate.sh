#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/template-prune/common.sh
source "${SCRIPT_DIR}/common.sh"

usage() {
  cat <<USAGE
Usage: scripts/template-prune/validate.sh <profile>

Profiles:
  no-rest
  no-graphql
  no-ios
  rest-only
USAGE
}

assert_missing() {
  local rel="$1"
  if [[ -e "${ROOT_DIR}/${rel}" ]]; then
    die "Expected path to be removed: ${rel}"
  fi
}

assert_not_contains() {
  local rel="$1"
  local regex="$2"
  local file="${ROOT_DIR}/${rel}"
  [[ -f "${file}" ]] || return 0

  if grep -Eq "${regex}" "${file}"; then
    die "Expected '${rel}' to not contain: ${regex}"
  fi
}

ensure_frontend_deps() {
  if [[ -d "${ROOT_DIR}/frontend" ]]; then
    run_task frontend:install
  fi
}

validate_no_rest() {
  assert_missing "backend/src/backend/apps/users/controllers.py"
  assert_missing "frontend/src/lib/restClient.ts"
  run_task backend:test
  ensure_frontend_deps
  run_task frontend:codegen
  run_task frontend:check
  run_task frontend:test:unit:run
}

validate_no_graphql() {
  assert_missing "backend/src/backend/graphql"
  assert_missing "frontend/src/lib/apollo"
  run_task backend:test
  ensure_frontend_deps
  run_task frontend:check
  run_task frontend:test:unit:run
}

validate_no_ios() {
  assert_missing "ios"
  assert_not_contains ".pre-commit-config.yaml" "ios-swiftlint"
  assert_not_contains "mise.toml" "^[[:space:]]*swiftlint[[:space:]]*="
  run_task backend:test
  if [[ -d "${ROOT_DIR}/frontend" ]]; then
    ensure_frontend_deps
    run_task frontend:check
  fi
}

validate_rest_only() {
  assert_missing "frontend"
  assert_missing "ios"
  assert_missing "backend/src/backend/graphql"
  assert_missing "backend/src/backend/celery_app.py"

  run_task backend:check
  run_task backend:typecheck
  run_task backend:test
}

main() {
  local profile="${1:-}"
  if [[ -z "${profile}" ]]; then
    usage
    exit 1
  fi

  case "${profile}" in
    no-rest) validate_no_rest ;;
    no-graphql) validate_no_graphql ;;
    no-ios) validate_no_ios ;;
    rest-only) validate_rest_only ;;
    *) usage; die "Unknown profile: ${profile}" ;;
  esac

  info "Validation completed for profile: ${profile}"
}

main "$@"
