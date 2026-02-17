---
name: remove-ios
description: Remove iOS app code, tooling, and references while preserving shared backend/frontend behavior.
---

Follow repo rules in:

- AGENTS.md
- .github/skills/guardrails/SKILL.md

Task:

- Remove all iOS source/assets/project files:
  - delete `ios/` directory.
  - delete `.agents/skills/swiftui-expert-skill/`.
- Remove iOS-specific rule files and routing:
  - delete `.github/instructions/swiftui.instructions.md`.
  - update `AGENTS.md` to remove iOS routing and iOS-specific precedence mentions.
- Remove iOS-specific workflows/tooling:
  - update `Taskfile.yml` to remove `IOS_TEST_DESTINATION` and `ios:test`.
  - update `mise.toml` to remove `swiftlint`.
  - update `.pre-commit-config.yaml` to remove `ios-swiftlint`.
  - update `.github/workflows/ci.yml` to remove the `ios-swiftlint` job.
  - update `.github/workflows/README.md` to remove iOS CI docs.
- Remove iOS references from project docs/instructions:
  - update `README.md` (badges, tech stack, prerequisites, iOS section,
    rules hierarchy mentions, and link refs).
  - update `.github/copilot-instructions.md` to remove iOS
    architecture/key-file references.
- Keep shared APIs unless proven unused:
  - do not remove `/api/auth/*` or `/api/users/me` endpoints if still used by frontend/backend/tests.
  - if considering backend endpoint removal, prove zero usage with `rg`
    across `backend/`, `frontend/`, and tests.
- Run a residual reference sweep and resolve project-owned leftovers:

  ```bash
  rg -n --hidden --glob '!.git' --glob '!frontend/pnpm-lock.yaml' --glob '!.github/prompts/remove-ios.prompt.md' -S 'ios/|\\biOS\\b|SwiftUI|swiftlint|xcodebuild|ios\\.xcodeproj|IOS_TEST_DESTINATION'
  ```

Constraints:

- Keep changes scoped to iOS decommissioning only.
- Do not refactor unrelated backend/frontend code.
- Do not change dependency versions except removing iOS-only tooling.
- If the residual sweep only finds incidental lockfile/base64 noise,
  document it and leave it unchanged.

Validation:

- `task backend:check`
- `task backend:typecheck`
- `task frontend:check`
- `task frontend:check:types`
- If any check cannot run, report exactly what was blocked and why.

Output:

- `Removed`: deleted files/directories.
- `Updated`: edited files.
- `Kept from iOS teardown`: functionality intentionally preserved and reason.
- `Validation`: commands run and pass/fail results.
- `Residual references`: any remaining iOS-related strings with justification.
