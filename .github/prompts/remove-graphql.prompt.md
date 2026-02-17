---
name: remove-graphql
description: Remove GraphQL from backend/frontend and keep REST + Celery.
---

Follow repo rules in:

- AGENTS.md
- .github/skills/guardrails/SKILL.md

Task:

- Remove backend GraphQL runtime and schema modules:
  - delete `backend/src/backend/graphql/`.
  - delete `backend/src/backend/apps/**/graphql/`.
  - update `backend/src/backend/application.py` to stop registering GraphQL
    controllers/context getters.
  - remove GraphQL-only settings/env (`graphql_max_depth`,
    `GRAPHQL_MAX_DEPTH`).
  - remove GraphQL path assumptions in auth/middleware if no longer needed.
- Remove backend GraphQL tests and fixtures:
  - delete `backend/tests/**/graphql/`.
  - update shared test fixtures that currently construct GraphQL context/client.
  - keep REST, admin, and rate-limit tests working.
- Remove frontend GraphQL client and contract artifacts:
  - delete `frontend/src/lib/apollo/`.
  - delete `frontend/src/lib/graphql/`.
  - delete `frontend/src/**/*.graphql`.
  - delete `frontend/schema/schema.graphql`.
  - delete `frontend/codegen.yml` and `frontend/codegen.schema.json`.
  - remove GraphQL/Apollo/codegen scripts and deps from
    `frontend/package.json`.
- Convert frontend UX to REST-only behavior:
  - remove GraphQL vs REST mode toggles and `dataSource` switching.
  - keep auth/profile/users flows functional via
    `frontend/src/lib/restClient.ts`.
  - stop deriving REST base URL from GraphQL env vars; use a dedicated REST
    env var and update env examples.
- Remove GraphQL workflow and CI glue:
  - remove `backend:schema:export` and `frontend:codegen` Taskfile tasks.
  - remove `schema:export` from `backend/Taskfile.yml`.
  - remove GraphQL schema verification from `.github/workflows/ci.yml`.
  - remove GraphQL codegen from `.github/actions/frontend-setup/action.yml`.
  - remove GraphQL bootstrap/log output in `setup.sh`.
- Remove GraphQL-adjacent project glue that is easy to miss:
  - update `backend/README.md` to remove GraphQL endpoint/docs references.
  - update `frontend/.gitignore`, `frontend/biome.json`, and
    `frontend/vitest.config.ts` to remove GraphQL artifact ignores/exclusions.
  - update `.vscode/extensions.json` to remove GraphQL extension
    recommendations if GraphQL is no longer a project workflow.
  - update frontend test setup/mocks that import Apollo:
    `frontend/__tests__/setup.tsx` and affected tests under `frontend/src/**`.
  - update `.github/copilot-instructions.md` and
    `.github/skills/guardrails/SKILL.md` to remove GraphQL-first assumptions.
- Remove GraphQL-specific docs/prompts/rules:
  - delete `.github/prompts/graphql-contract.prompt.md`.
  - delete `.github/skills/graphql-contract/SKILL.md`.
  - update `.github/instructions/*.instructions.md` and prompt files that
    currently require GraphQL.
  - update README/docs to describe REST-only API usage.
- Keep worker/Celery infrastructure intact:
  - do not remove or rename `backend/src/backend/celery_app.py`.
  - keep `task worker:dev`, `task beat:dev`, and `task flower:dev`.
  - keep Celery/Flower dependencies and configuration.
- Use Taskfile dependency wrappers when removing direct GraphQL dependencies:
  - backend: `task backend:dep:remove -- strawberry-graphql`
  - backend dev: `task backend:dep:remove:dev -- strawberry-graphql`
  - frontend runtime/dev: use `task frontend:dep:remove` /
    `task frontend:dep:remove:dev` for GraphQL/Apollo/codegen packages.
- Run a residual GraphQL reference sweep and resolve project-owned leftovers:

  ```bash
  rg -n --hidden --glob '!.git' \
    --glob '!backend/uv.lock' \
    --glob '!frontend/pnpm-lock.yaml' \
    --glob '!.github/prompts/remove-graphql.prompt.md' \
    -S 'GraphQL|graphql|strawberry|/graphql|schema\\.graphql|codegen'
  ```

Constraints:

- Keep changes scoped to GraphQL removal only.
- Do not remove REST endpoints, controllers, or REST client behavior.
- Do not remove worker/beat/flower code paths.
- Do not remove `msw` or `msw-storybook-addon`.
- `graphql` may remain only when required as a peer/transitive dependency for
  `msw`/`msw-storybook-addon`; remove GraphQL API usage instead.
- Do not edit generated lockfiles manually.
- If residual references are lockfile-only or due to `msw`/`msw-storybook-addon`
  dependency trees, document and keep them.

Validation:

- `task backend:check`
- `task backend:typecheck`
- `task backend:test`
- `task frontend:check`
- `task frontend:check:types`
- `task frontend:test:unit:run`
- If a check cannot run, report the blocker with exact command and reason.

Output:

- `Removed`: deleted files/directories.
- `Updated`: edited files.
- `Preserved`: REST and Celery/worker paths intentionally kept.
- `Validation`: commands run and pass/fail results.
- `Residual references`: any remaining GraphQL strings with justification.
