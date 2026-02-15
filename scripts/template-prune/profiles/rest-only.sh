#!/usr/bin/env bash
set -euo pipefail

profile_summary() {
  local out="$1"
  cat > "${out}" <<SUMMARY
remove frontend and ios directories
remove GraphQL backend modules and GraphQL tests
remove Celery/Beat/Flower modules, tests, and dependencies
remove Redis service and worker/beat/flower tasks
rewrite setup/docs/CI/taskfiles for backend REST + Postgres only
set terminal prune profile to rest-only
SUMMARY
}

profile_apply() {
  remove_path "frontend"
  remove_path "ios"

  remove_path "backend/src/backend/graphql"
  remove_path "backend/src/backend/apps/users/graphql"
  remove_path "backend/tests/apps/users/graphql"
  remove_path "backend/tests/graphql"

  remove_path "backend/src/backend/celery_app.py"
  remove_path "backend/src/backend/apps/users/tasks.py"
  remove_path "backend/tests/apps/users/test_tasks.py"

  copy_template_file "no-graphql" "backend/src/backend/application.py"
  copy_template_file "no-graphql" "backend/src/backend/auth/jwt.py"
  copy_template_file "rest-only" "backend/src/backend/config/base.py"
  copy_template_file "rest-only" "backend/src/backend/admin/views/user.py"
  copy_template_file "rest-only" "backend/Taskfile.yml"
  copy_template_file "rest-only" "backend/.env.example"

  copy_template_file "rest-only" "Taskfile.yml"
  copy_template_file "rest-only" "compose.yaml"
  copy_template_file "rest-only" "setup.sh"
  copy_template_file "rest-only" "README.md"
  copy_template_file "rest-only" ".github/workflows/ci.yml"
  copy_template_file "rest-only" ".github/workflows/README.md"
  copy_template_file "rest-only" ".github/copilot-instructions.md"

  remove_path ".github/actions/frontend-setup"
  remove_path ".github/prompts/frontend-feature.prompt.md"
  remove_path ".github/prompts/graphql-contract.prompt.md"
  remove_path ".github/skills/graphql-contract"
  remove_path ".github/instructions/frontend.instructions.md"
  remove_path ".github/instructions/typescript.instructions.md"
  remove_path ".github/instructions/swiftui.instructions.md"

  run_task backend:dep:remove -- "strawberry-graphql celery flower"
  run_task backend:dep:remove:dev -- "strawberry-graphql"

  set_state_bool "has_graphql" "false"
  set_state_bool "has_frontend" "false"
  set_state_bool "has_ios" "false"
  set_state_bool "has_celery" "false"
  set_state_bool "has_redis" "false"
  set_state_bool "has_rest" "true"
  set_state_string "terminal_profile" "rest-only"
}
