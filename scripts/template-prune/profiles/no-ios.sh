#!/usr/bin/env bash
set -euo pipefail

profile_summary() {
  local out="$1"
  cat > "${out}" <<SUMMARY
remove ios/
remove SwiftUI skill (.agents/skills/swiftui-expert-skill)
remove SwiftUI instruction file (.github/instructions/swiftui.instructions.md)
remove iOS root task (Taskfile.yml: ios:test)
remove iOS root task var (Taskfile.yml: IOS_TEST_DESTINATION)
remove iOS CI job (.github/workflows/ci.yml: ios-swiftlint)
remove iOS pre-commit hook (.pre-commit-config.yaml: ios-swiftlint)
remove SwiftLint tool pin (mise.toml: swiftlint)
remove iOS routing references in AGENTS.md
remove iOS docs sections/references in README and .github docs
SUMMARY
}

profile_apply() {
  remove_path "ios"
  remove_path ".agents/skills/swiftui-expert-skill"
  remove_path ".github/instructions/swiftui.instructions.md"

  remove_root_task_block "Taskfile.yml" "ios:test"
  remove_regex_lines "Taskfile.yml" "^[[:space:]]*IOS_TEST_DESTINATION:"

  replace_in_file \
    ".github/workflows/ci.yml" \
    "\\n  ios-swiftlint:[\\s\\S]*?        run: swiftlint\\n" \
    "\n"

  replace_in_file \
    ".pre-commit-config.yaml" \
    "\\n      - id: ios-swiftlint[\\s\\S]*?        files: \\^ios\\/\\n" \
    "\n"

  remove_regex_lines "mise.toml" "^[[:space:]]*swiftlint[[:space:]]*="

  replace_in_file \
    "AGENTS.md" \
    '\n- `ios/`: apply\n  \[`.github/instructions/swiftui.instructions.md`\]\(.github/instructions/swiftui.instructions.md\)\.\n' \
    "\n"
  replace_in_file \
    "AGENTS.md" \
    '`backend/AGENTS.md`, `frontend/AGENTS.md`, or `ios/AGENTS.md` over this file' \
    '`backend/AGENTS.md` or `frontend/AGENTS.md` over this file'

  replace_in_file "README.md" "\\n!\\[Swift\\]\\([^\\n]*\\)\\n" "\n"
  replace_in_file "README.md" "\\n!\\[iOS\\]\\([^\\n]*\\)\\n" "\n"
  replace_in_file \
    "README.md" \
    "TypeScript \\(Next\\.js\\) frontend, connected via GraphQL and REST, plus an optional\\nSwiftUI iOS client\\. Ideal for hackathons and rapid prototyping, designed to\\n" \
    "TypeScript (Next.js) frontend, connected via GraphQL and REST. Ideal for hackathons and rapid prototyping, designed to\\n"
  replace_in_file "README.md" "\\n[[:space:]]*- \\[Mobile \\(iOS\\)\\]\\(#mobile-ios\\)\\n" "\n"
  replace_in_file "README.md" "\\n[[:space:]]*- \\[📱 iOS App\\]\\(#-ios-app\\)\\n" "\n"
  replace_in_file \
    "README.md" \
    "\\n### Mobile \\(iOS\\)\\n[\\s\\S]*?\\n## 🚀 Getting Started\\n" \
    "\n## 🚀 Getting Started\n"
  remove_regex_lines "README.md" "for iOS development"
  replace_in_file \
    "README.md" \
    "\\n## 📱 iOS App\\n[\\s\\S]*?\\n## 📏 Rules System\\n" \
    "\n## 📏 Rules System\n"
  replace_in_file \
    "README.md" \
    '\n- \[`ios/AGENTS.md`\]\(ios/AGENTS.md\) provides iOS-local scoping while still\n  delegating to the canonical instruction files\.\n' \
    "\n"
  replace_in_file \
    "README.md" \
    "removes GraphQL, frontend, iOS, Celery/Beat/Flower, and Redis\\." \
    "removes GraphQL, frontend, Celery/Beat/Flower, and Redis."
  replace_in_file "README.md" "\\n\\[swift\\]: https://www\\.swift\\.org/\\n" "\n"
  replace_in_file "README.md" "\\n\\[swiftui\\]: https://developer\\.apple\\.com/swiftui/\\n" "\n"
  replace_in_file "README.md" "\\n\\[xcode\\]: https://developer\\.apple\\.com/xcode/\\n" "\n"
  remove_regex_lines ".github/workflows/README.md" "iOS SwiftLint|SwiftLint"
  remove_regex_lines ".github/copilot-instructions.md" "iOS|SwiftUI|ios/"
  replace_in_file "AGENTS.md" "\\n{3,}" "\n\n"
  replace_in_file ".pre-commit-config.yaml" "\\n{3,}" "\n\n"
  replace_in_file "README.md" "\\n{3,}" "\n\n"
  replace_in_file ".github/workflows/README.md" "\\n{3,}" "\n\n"
  replace_in_file ".github/copilot-instructions.md" "\\n{3,}" "\n\n"

  set_state_bool "has_ios" "false"
}
