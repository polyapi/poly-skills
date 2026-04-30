# AGENTS Guide for Canopy

This pack is for agents working in the Canopy UI repository and on PolyAPI-backed
Canopy application configuration. Keep this file focused on repo-wide rules.
Task-specific workflows live under `./.agents/skills/*/SKILL.md`; detailed
project facts live under `./.agents/skills/*/references/REFERENCE.md`.

## Scope

- Applies to Canopy UI work in `src/`.
- Applies to PolyAPI application config under `polyapi_config/`.
- Applies to collection config, generated/config artifacts, auth/session work,
  access logs, function execution, role-gated UI, and deployment.
- Does not replace checked-in implementation. If this pack conflicts with code,
  follow the code and document the drift.

## Source of Truth

1. This `AGENTS.md` for shared repo-wide rules
2. Existing checked-in Canopy implementation
3. Existing checked-in PolyAPI config and generated/config artifacts
4. Relevant local skills under `./.agents/skills/`
5. Runtime/deployment behavior captured in `./.agents/skills/*/references/`
6. README or other documentation
7. General framework knowledge

## Repo-Wide Rules

- Inspect JSON/config first for collection UI behavior.
- For collection-backed features, list `polyapi_config/collections/`, choose
  the folder matching the URL segment, then inspect that folder's
  `collection.json` and `api.json` when present.
- Prefer config changes before React/TypeScript changes when the behavior is
  intended to be collection-driven.
- Reuse existing config patterns, shared components, helper functions, and data
  flows before introducing new abstractions.
- Do not serialize empty optional query params or body fields when the backend
  expects the field to be absent. Check `src/api/poly/function.ts` and
  `removeIfNotPresentOnExecute` behavior.
- Keep frontend config, runtime request construction, backend validation, and
  displayed UI behavior aligned.
- Keep generic route/page TSX files generic. Do not hardcode one collection,
  action label, or function path in a generic renderer unless explicitly
  approved.
- For larger or logic-heavy UI additions, prefer extracting them into a
  separate component and mounting them only when active. Treat this as a render
  boundary so expensive state, effects, and computations do not run on the
  default path. Use useMemo, useCallback, and React.memo only when profiling
  confirms a real dependency or re-render bottleneck.
- Verify role/security implications before changing visibility, editability,
  filters, logs, auth, or session behavior.
- Never expose secrets, API keys, OTP/MFA tokens, credentials, private keys,
  certificates, or sensitive customer data. Avoid reading `.env`, key, cert, or
  secret files unless the task explicitly requires it and it is safe.
- Frontend hiding is not security. Preserve tenant boundaries and validate
  server-side enforcement for sensitive changes.
- Treat auth, access logs, user roles, role-based display, MFA, and API key
  behavior as security-sensitive areas.

## Deployment Rule

After merging changes to a `collection.json` file or one of its associated
`api.json` files, manually run the GitHub workflow to deploy the new PolyUI
application targeting `develop`:

[Canopy update PolyAPI app config workflow](https://github.com/polyapi/canopy/actions/workflows/canopy-update-polyapi-app-config.yml)

This manual workflow is required anytime Canopy collection config or associated
API config changes.

## Task Entry Points

- Use `./.agents/skills/canopy-core/SKILL.md` when onboarding, mapping source
  ownership, planning cross-layer Canopy work, or checking PolyUI config
  deployment requirements.
- Use `./.agents/skills/canopy-config-ui-runtime/SKILL.md` before changing
  collection config, filters, fields, actions, generic UI rendering,
  execute-function pages, collection CRUD, or runtime request mapping.
- Use `./.agents/skills/canopy-security-auth/SKILL.md` before changing auth,
  sessions, access logs, roles, permissions, visibility, MFA, API keys, tenant
  isolation, or other security-sensitive UI/runtime behavior.
- If installed, use `./.agents/skills/design-analysis/SKILL.md` as soon as a
  target PolyAPI design is provided.
- If installed, use `./.agents/skills/markdownlint-compliance/SKILL.md` when
  editing Markdown.
- Use `README.md` for setup and local tooling.

## Important Entry Points

PolyAPI config:

- `polyapi_config/collections/<collection>/collection.json` - UI-facing
  collection config. `<collection>` is the folder name and matches the
  collection segment in URLs like
  `/<appId>/collections/<collection>/<itemId>/...`. There are many collection
  folders and they are all equally important; always re-list the directory and
  pick the one(s) matching the URL or feature.
- `polyapi_config/collections/<collection>/api.json` - optional PolyAPI
  function/gateway contract for that same collection. Read it with
  `collection.json` when it exists; some collections are config-only.
- `polyapi_config/collections/all_collections.js` - deployed collection list
  and sidebar ordering.
- `polyapi_config/collections/autogen_apis.js` - autogen collection list paired
  with `polyapi_config/autogen_apis/` and `api-generator.js`.
- `polyapi_config/misc_apis.json` - shared/login/signup API specs not owned by
  a single collection.
- `polyapi_config/app_base.json` - PolyUI canopy app base config (login/signup
  screens, sidebar, defaults).
- `polyapi_config/overlays/api.v1.json`, `api.v2.json` - overlay defaults
  applied during API spec generation.
- `polyapi_config/build_and_deploy.js`, `deploy_envs.js`, `env_overrides.js` -
  build, deploy targeting, and per-env overrides.
- `client_apps/<app>/application.json` - example custom canopy app configs.

Server-side API helpers (`src/api`):

- `src/api/session.ts` - session cookie management
  (`COOKIE_NAME_SESSION_ID`, `POLY_COOKIE_SESSION_ID`, basePath-aware).
- `src/api/poly/auth.ts` - API key and session/auth data lookup.
- `src/api/poly/common.ts` - fetch helpers, `processResponse`,
  `RawResponseHolder`, `getWithAuth`.
- `src/api/poly/config.ts` - app config loading and normalization.
- `src/api/poly/function.ts` - function execution, `getExecutionBody`, empty
  optional value handling, raw function execution, MFA header transport.
- `src/api/poly/collection.ts` - collection CRUD/list orchestration and
  access-log merge behavior.
- `src/api/poly/page.ts` - `submitPage` for item subpages, execute-function,
  and trigger-webhook page submissions.
- `src/api/poly/webhook.ts` - `triggerWebhookHandle` direct webhook calls.
- `src/api/poly/app.ts`, `whoami.ts`, `metrics.ts` - app list, current user,
  and execution metrics.
- `src/api/poly/types.ts`, `constants.ts` - auth, role, session, and function
  type contracts.

Lib utilities (`src/lib`):

- `src/lib/session.ts` - JWT-encrypted sessions in Redis (`createSession`,
  `refreshSession`, `idleTimeout`/`maxTimeout` enforcement).
- `src/lib/redis.ts` - ioredis client with optional TLS certs from `./tls/`.
- `src/lib/sandbox.ts` - sandboxed evaluation of dynamic property expressions
  (`item`, `data`, `params`, `query`, `auth`, `path`).
- `src/lib/template.ts` - `{{path}}` template interpolation.
- `src/lib/types.ts`, `constants.ts`, `errors.ts`, `utils.ts` - shared types,
  cookie names, error helpers.

UI (`src/app`, `src/components`):

- `src/middleware.ts` - request logging and `x-url` header injection.
- `src/app/[appId]/collections/[collectionId]/...` - generic collection list,
  detail, edit, create, item subpages, execute-function, trigger-webhook, and
  delete modal routes.
- `src/app/[appId]/auth/[[...params]]` - auth callback catch-all (incl.
  `expired`, `expiring`, `rotated`, `finish-oauth`, `choose-environment`).
- `src/app/[appId]/forms/[formId]` - standalone configured forms.
- `src/app/about-me/*` - About Me SSR page and dialog.
- `src/components/collection/*` - generic property rendering, form fields,
  filters, list item properties, typed fields.
- `src/components/action-bar/*` - generic action/filter bar, menus, and action
  execution controls (including `MfaActionButton`).
- `src/components/auth/MfaTokenDialog.tsx`, `MfaTokenInput.tsx` - MFA prompt UI.
- `src/components/session/actions.ts`, `IdleHandler.tsx`, `LogoutButton.tsx` -
  login/session actions, idle-timeout handler, logout, and access-log writes.
- `src/components/custom/execute-function/*` - execute-function argument UI,
  variable arguments, saved-request helpers.
- `src/components/app-switcher/*`, `hoc/*`, `form/*`, `pager/*`,
  `theme-*/*`, `ui/*` - generic shell, HOCs, form scaffolding, pagination,
  theming, and primitive UI components.

CI/infra:

- `.github/workflows/canopy-ci.yml` - lint, test, type-check.
- `.github/workflows/canopy-docker-image.yml` - container image build.
- `.github/workflows/canopy-update-polyapi-app-config.yml` - manual PolyUI
  app config deploy.
- `.github/workflows/customer_release.yaml` - customer release flow.
- `docker/Dockerfile`, `docker/scripts/*` - container build and entrypoint.
