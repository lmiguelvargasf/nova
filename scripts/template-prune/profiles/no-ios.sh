#!/usr/bin/env bash
set -euo pipefail

profile_summary() {
  local out="$1"
  cat > "${out}" <<SUMMARY
remove ios/
remove SwiftUI skill (.agents/skills/swiftui-expert-skill)
remove iOS root task (Taskfile.yml: ios:test)
remove iOS CI job (.github/workflows/ci.yml: ios-swiftlint)
remove iOS pre-commit hook (.pre-commit-config.yaml: ios-swiftlint)
remove SwiftLint tool pin (mise.toml: swiftlint)
remove iOS docs references in README and .github docs
SUMMARY
}

profile_apply() {
  remove_path "ios"
  remove_path ".agents/skills/swiftui-expert-skill"

  remove_root_task_block "Taskfile.yml" "ios:test"

  replace_in_file \
    ".github/workflows/ci.yml" \
    "\\n  ios-swiftlint:[\\s\\S]*?        run: swiftlint\\n" \
    "\n"

  replace_in_file \
    ".pre-commit-config.yaml" \
    "\\n      - id: ios-swiftlint[\\s\\S]*?        files: \\^ios\\/\\n" \
    "\n"

  remove_regex_lines "mise.toml" "^[[:space:]]*swiftlint[[:space:]]*="

  remove_regex_lines "README.md" "iOS|SwiftUI|Xcode|SwiftLint|ios/"
  remove_regex_lines ".github/workflows/README.md" "iOS SwiftLint|SwiftLint"
  remove_regex_lines ".github/copilot-instructions.md" "iOS|SwiftUI|ios/"
  replace_in_file ".pre-commit-config.yaml" "\\n{3,}" "\n\n"
  replace_in_file "README.md" "\\n{3,}" "\n\n"
  replace_in_file ".github/workflows/README.md" "\\n{3,}" "\n\n"
  replace_in_file ".github/copilot-instructions.md" "\\n{3,}" "\n\n"

  set_state_bool "has_ios" "false"
}
