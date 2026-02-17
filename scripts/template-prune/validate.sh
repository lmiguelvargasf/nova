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
  assert_missing "frontend/codegen.yml"
  assert_missing "frontend/codegen.schema.json"
  assert_missing ".github/prompts/graphql-contract.prompt.md"
  assert_missing ".github/skills/graphql-contract"

  assert_not_contains "backend/Taskfile.yml" "schema:export|backend\\.graphql\\.schema|GraphQL schema"
  assert_not_contains "backend/.env.example" "GRAPHQL_MAX_DEPTH"
  assert_not_contains "backend/README.md" "GraphQL|/graphql"
  assert_not_contains "backend/pyproject.toml" "\"\\*\\*/graphql/\\*\\*/\\*\\.py\""
  assert_not_contains "frontend/package.json" "graphql-codegen|\"prebuild\"[[:space:]]*:[[:space:]]*\"pnpm codegen\"|\"codegen\"[[:space:]]*:|\"codegen:watch\"[[:space:]]*:"
  assert_not_contains "frontend/vitest.config.ts" "GraphQL files|src/lib/graphql/\\*\\*|schema/schema\\.graphql"
  assert_not_contains "frontend/.gitignore" "GraphQL Codegen|/src/lib/graphql/"
  assert_not_contains "frontend/biome.json" "src/lib/graphql|schema/schema\\.graphql"
  assert_not_contains "setup.sh" "Running codegen"
  assert_not_contains "setup.sh" "run_task_if_present frontend:codegen"
  assert_not_contains "setup.sh" "GraphQL:[[:space:]]+http://localhost:8000/graphql"
  assert_not_contains ".github/workflows/README.md" "GraphQL|codegen"
  assert_not_contains ".github/instructions/backend.instructions.md" "GraphQL|graphql"
  assert_not_contains ".github/instructions/frontend.instructions.md" "GraphQL|graphql"
  assert_not_contains ".github/instructions/typescript.instructions.md" "GraphQL|graphql"
  assert_not_contains ".github/instructions/python.instructions.md" "GraphQL|graphql"
  assert_not_contains ".github/prompts/backend-entity.prompt.md" "GraphQL|graphql"
  assert_not_contains ".github/prompts/frontend-feature.prompt.md" "GraphQL|graphql"
  assert_not_contains ".github/skills/guardrails/SKILL.md" "GraphQL|graphql"

  run_task backend:test
  ensure_frontend_deps
  run_task frontend:check
  run_task frontend:test:unit:run
}

validate_no_ios() {
  assert_missing "ios"
  assert_missing ".agents/skills/swiftui-expert-skill"
  assert_missing ".github/instructions/swiftui.instructions.md"
  assert_not_contains ".pre-commit-config.yaml" "ios-swiftlint"
  assert_not_contains "mise.toml" "^[[:space:]]*swiftlint[[:space:]]*="
  assert_not_contains "Taskfile.yml" "IOS_TEST_DESTINATION"
  assert_not_contains "AGENTS.md" '`ios/`: apply'
  assert_not_contains "AGENTS.md" "swiftui.instructions.md"
  assert_not_contains "AGENTS.md" "ios/AGENTS.md"
  assert_not_contains "README.md" "### Mobile \\(iOS\\)"
  assert_not_contains "README.md" "## 📱 iOS App"
  assert_not_contains "README.md" "\\[Mobile \\(iOS\\)\\]\\(#mobile-ios\\)"
  assert_not_contains "README.md" "\\[📱 iOS App\\]\\(#-ios-app\\)"
  assert_not_contains "README.md" "^!\\[Swift\\]"
  assert_not_contains "README.md" "^!\\[iOS\\]"
  assert_not_contains "README.md" "^2\\. Select a simulator or device\\.$"
  assert_not_contains "README.md" "^\\[(swift|swiftui|xcode)\\]:"
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
