#!/usr/bin/env bash
set -euo pipefail

profile_summary() {
  local out="$1"
  cat > "${out}" <<SUMMARY
remove backend REST controllers/schemas/pagination and REST tests
patch backend app wiring and auth excludes for GraphQL-only runtime
remove frontend REST client and data-source toggle logic
patch mixed frontend pages/components to GraphQL-only templates
SUMMARY
}

profile_apply() {
  remove_path "backend/src/backend/apps/users/controllers.py"
  remove_path "backend/src/backend/apps/users/schemas.py"
  remove_path "backend/src/backend/apps/users/pagination.py"
  remove_path "backend/src/backend/api/pagination.py"
  remove_path "backend/tests/apps/users/rest"
  remove_path "backend/tests/auth/test_jwt.py"

  copy_template_file "no-rest" "backend/src/backend/application.py"
  copy_template_file "no-rest" "backend/src/backend/auth/jwt.py"

  remove_path "frontend/src/lib/restClient.ts"
  remove_path "frontend/src/lib/dataSource.ts"

  copy_template_file "no-rest" "frontend/src/features/auth/LoginForm.tsx"
  copy_template_file "no-rest" "frontend/src/features/auth/RegisterForm.tsx"
  copy_template_file "no-rest" "frontend/src/features/users/CurrentUserCard.client.tsx"
  copy_template_file "no-rest" "frontend/src/features/users/UsersPaginationCard.client.tsx"
  copy_template_file "no-rest" "frontend/src/app/profile/page.tsx"
  copy_template_file "no-rest" "frontend/src/app/page.tsx"

  remove_regex_lines "README.md" "REST|rest"
  remove_regex_lines ".github/copilot-instructions.md" "REST|rest"

  set_state_bool "has_rest" "false"
}
