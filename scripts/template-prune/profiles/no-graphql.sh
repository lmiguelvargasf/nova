#!/usr/bin/env bash
set -euo pipefail

profile_summary() {
  local out="$1"
  cat > "${out}" <<SUMMARY
remove backend GraphQL modules and GraphQL tests
remove frontend GraphQL modules, Apollo client wiring, GraphQL documents/codegen
patch backend and frontend mixed files to REST-only templates
remove GraphQL codegen tasks and CI schema verification steps
remove GraphQL-specific prompts/skills references
SUMMARY
}

profile_apply() {
  remove_path "backend/src/backend/graphql"
  remove_path "backend/src/backend/apps/users/graphql"
  remove_path "backend/tests/apps/users/graphql"
  remove_path "backend/tests/graphql"

  copy_template_file "no-graphql" "backend/src/backend/application.py"
  copy_template_file "no-graphql" "backend/src/backend/auth/jwt.py"
  copy_template_file "no-graphql" "backend/src/backend/config/base.py"
  copy_template_file "no-graphql" "backend/tests/conftest.py"
  copy_template_file "no-graphql" "backend/tests/middleware/test_rate_limit.py"
  copy_template_file "no-graphql" "backend/tests/admin/test_app.py"

  remove_path "frontend/src/lib/apollo"
  remove_path "frontend/src/lib/graphql"
  remove_path "frontend/src/lib/dataSource.ts"
  remove_path "frontend/schema/schema.graphql"
  remove_path "frontend/codegen.yml"
  remove_path "frontend/codegen.schema.json"

  remove_path "frontend/src/features/auth/Login.graphql"
  remove_path "frontend/src/features/users/CreateUser.graphql"
  remove_path "frontend/src/features/users/GetMe.graphql"
  remove_path "frontend/src/features/users/GetUserById.graphql"
  remove_path "frontend/src/features/users/GetUsersPage.graphql"
  remove_path "frontend/src/features/users/SoftDeleteCurrentUser.graphql"
  remove_path "frontend/src/features/users/UpdateCurrentUser.graphql"

  remove_path "frontend/src/features/users/UserCard.client.tsx"
  remove_path "frontend/src/features/users/UserCard.test.tsx"
  remove_path "frontend/src/features/users/UserCreator.client.tsx"
  remove_path "frontend/src/features/users/UserCreator.stories.tsx"

  copy_template_file "no-graphql" "frontend/src/lib/restClient.ts"
  copy_template_file "no-graphql" "frontend/src/app/layout.tsx"
  copy_template_file "no-graphql" "frontend/src/app/page.tsx"
  copy_template_file "no-graphql" "frontend/src/app/profile/page.tsx"
  copy_template_file "no-graphql" "frontend/src/features/auth/LoginForm.tsx"
  copy_template_file "no-graphql" "frontend/src/features/auth/RegisterForm.tsx"
  copy_template_file "no-graphql" "frontend/src/features/users/CurrentUserCard.client.tsx"
  copy_template_file "no-graphql" "frontend/src/features/users/UsersPaginationCard.client.tsx"
  copy_template_file "no-graphql" "frontend/src/app/page.test.tsx"
  copy_template_file "no-graphql" "frontend/__tests__/setup.tsx"
  copy_template_file "no-graphql" "frontend/.env.local.example"

  remove_root_task_block "frontend/Taskfile.yml" "codegen"
  remove_root_task_block "Taskfile.yml" "backend:schema:export"
  remove_root_task_block "Taskfile.yml" "frontend:codegen"

  replace_in_file \
    ".github/actions/frontend-setup/action.yml" \
    "\\n    - name: Generate GraphQL Code[\\s\\S]*?run: pnpm codegen\\n" \
    "\n"

  replace_in_file \
    ".github/workflows/ci.yml" \
    "\\n  verify-schema:[\\s\\S]*?\\n\\s*fi\\n" \
    "\n"

  remove_regex_lines "README.md" "GraphQL|graphql-contract|frontend:codegen|schema:export|/graphql"
  remove_regex_lines ".github/workflows/README.md" "GraphQL|codegen"
  remove_regex_lines ".github/copilot-instructions.md" "GraphQL|graphql"
  remove_regex_lines ".vscode/extensions.json" "graphql\\.vscode-graphql"

  replace_in_file "README.md" "\\n{3,}" "\n\n"
  replace_in_file ".github/workflows/README.md" "\\n{3,}" "\n\n"
  replace_in_file ".github/copilot-instructions.md" "\\n{3,}" "\n\n"

  remove_path ".github/prompts/graphql-contract.prompt.md"
  remove_path ".github/skills/graphql-contract"

  run_task frontend:dep:remove -- @apollo/client @apollo/client-integration-nextjs graphql
  run_task frontend:dep:remove:dev -- @graphql-codegen/cli @graphql-codegen/typescript @graphql-codegen/typescript-operations @graphql-codegen/typescript-react-apollo @graphql-typed-document-node/core
  run_task backend:dep:remove -- "strawberry-graphql"
  run_task backend:dep:remove:dev -- "strawberry-graphql"

  set_state_bool "has_graphql" "false"
}
