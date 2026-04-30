# Canopy Core Reference

## Source of Truth

1. Existing checked-in Canopy implementation
2. Existing checked-in PolyAPI config and generated/config artifacts
3. Runtime/deployment behavior captured in local skill references
4. Existing skill project structure in `./poly-skills`
5. README and other documentation
6. General framework knowledge

If documentation conflicts with implementation, follow implementation and
document the drift.

## Source Map

| Area | Files/folders | Responsibility |
| --- | --- | --- |
| Next.js shell | `src/app/layout.tsx`, `src/app/page.tsx`, `src/app/error.tsx`, `src/app/loading.tsx`, `src/app/not-found.tsx`, `src/middleware.ts` | Root layout, app launch screen, error/loading boundaries, request logging |
| App routes | `src/app/[appId]/*` | Per-application Next.js route tree: `collections/`, `auth/`, `login/`, `signup/`, `forms/`, `not-found/`, `unauthorized/` |
| Collection routes | `src/app/[appId]/collections/[collectionId]/...` | Generic list/detail/edit/create, item subpages (`[pageId]`), execute API/server function, trigger-webhook, delete modal (`@modal/`) |
| Forms route | `src/app/[appId]/forms/[formId]` | Standalone configured forms with their own action/refresh layout |
| About Me | `src/app/about-me/*` | SSR About Me page and client dialog |
| API helpers | `src/api/poly/*` (`auth.ts`, `app.ts`, `collection.ts`, `common.ts`, `config.ts`, `constants.ts`, `function.ts`, `metrics.ts`, `page.ts`, `types.ts`, `webhook.ts`, `whoami.ts`) | Config loading, auth, fetch helpers, function execution, collection CRUD, page submit, raw webhook, metrics, types |
| Session cookies | `src/api/session.ts` | Cookie names, basePath-aware paths, default-app session shadow cookie |
| Lib | `src/lib/*` (`session.ts`, `redis.ts`, `sandbox.ts`, `template.ts`, `constants.ts`, `errors.ts`, `localStorage.ts`, `recaptcha.ts`, `types.ts`, `utils.ts`) | JWT/Redis sessions, sandboxed dynamic expressions, template interpolation, error helpers |
| Hooks | `src/hooks/*`, `src/components/hooks/*` | `useAuth`, `useRefState`, `useMediaQuery` |
| Collection rendering | `src/components/collection/*` | Generic property rendering, forms, filters, item cards, typed fields (`*TypeField.tsx`), `DetailsPage`, `CollectionList`, `GroupedCollections` |
| Action rendering | `src/components/action-bar/*` | `ActionBar`, `ActionBarMenu`, `FunctionActionButton`, `MfaActionButton`, `ClearFiltersButton` |
| Auth UI | `src/components/auth/*` | `MfaTokenDialog`, `MfaTokenInput` |
| Session UI | `src/components/session/*` | `actions.ts` (login/session/access-log), `IdleHandler`, `LogoutButton` |
| Execute function UI | `src/components/custom/execute-function/*` | API/server function execute arguments, `FunctionVariableArgument`, saved-request helpers |
| App shell | `src/components/app-switcher/*`, `hoc/*`, `form/*`, `pager/*`, `theme-*/*`, `loading/*`, `empty/*`, `errors/*`, `ui/*`, `utils/*` | Sidebar app switcher, HOCs (`withAuth`, `withError`, `withSuspense`), form scaffolding, pagination, theming, primitives |
| Canopy app config | `polyapi_config/*` | PolyUI app base config, collection configs, API specs, deploy script, env overrides, overlays, autogen APIs |
| Collection registry | `polyapi_config/collections/all_collections.js`, `polyapi_config/collections/autogen_apis.js` | Which collections deploy and their sidebar order; autogen API list |
| Other client apps | `client_apps/<app>/application.json` | Example custom canopy app configs |
| CI/deploy | `.github/workflows/*` | `canopy-ci.yml`, `canopy-docker-image.yml`, `canopy-update-polyapi-app-config.yml`, `customer_release.yaml` |
| Container | `docker/Dockerfile`, `docker/scripts/*` | Container build and entrypoint |

## Main Runtime Flow

1. `src/middleware.ts` logs requests and forwards an `x-url` header.
2. `src/api/session.ts` reads the session cookie (`COOKIE_NAME_SESSION_ID`,
   with `POLY_COOKIE_SESSION_ID` shadow for the default app).
3. `src/lib/session.ts` decrypts the session JWT from Redis and may refresh
   TTL based on `idleTimeout` and `maxTimeout` from the session config.
4. `src/api/poly/config.ts` fetches application config from
   `/applications/{appSubpath}/config` and normalizes collection config.
5. Dynamic routes under `src/app/[appId]/collections/...` locate the
   collection by `collectionId`.
6. Generic pages render `ActionBar`, filters, item cards, details, forms,
   item pages, and subcollections from collection config.
7. Collection operations in `src/api/poly/collection.ts` call helpers in
   `src/api/poly/function.ts`.
8. `getExecutionBody` maps session, path params, query params, item data,
   static values, variables, and MFA into execution bodies.
9. Function execution goes through either the Poly function gateway (`api`,
   `server`, `query`) or a direct raw URL (`raw`).
10. `src/api/poly/page.ts` (`submitPage`) handles item subpage / execute /
    trigger-webhook submissions reusing the same execution helpers.
11. `src/lib/sandbox.ts` evaluates dynamic property expressions with `item`,
    `data`, `params`, `query`, `auth`, `path`.
12. `src/lib/template.ts` interpolates `{{path}}` placeholders for URL/label
    templating.

## Deployment

Manual workflow required after merging `collection.json` or associated
`api.json` changes:

[Canopy update PolyAPI app config workflow](https://github.com/polyapi/canopy/actions/workflows/canopy-update-polyapi-app-config.yml)

Target: `develop`.

Important files:

- `.github/workflows/canopy-update-polyapi-app-config.yml`
- `.github/workflows/canopy-ci.yml`
- `.github/workflows/canopy-docker-image.yml`
- `.github/workflows/customer_release.yaml`
- `polyapi_config/build_and_deploy.js`
- `polyapi_config/api-generator.js`
- `polyapi_config/app_base.json`
- `polyapi_config/misc_apis.json`
- `polyapi_config/env_overrides.js`
- `polyapi_config/deploy_envs.js`
- `polyapi_config/collections/all_collections.js`
- `polyapi_config/collections/autogen_apis.js`
- `polyapi_config/overlays/api.v1.json`, `api.v2.json`
- `docker/Dockerfile`, `docker/scripts/*`

Deploy script behavior:

- Loads `app_base.json`.
- Applies environment overrides from `env_overrides.js` for the configured
  `DEPLOY_ENV` (`localhost`, `develop`, `na1`, `eu1`, ...) or
  `POLY_API_BASE_URL`.
- Reads collections in `ALL_COLLECTIONS` order; autogen collections come from
  `AUTOGEN_APIS` and are generated via `api-generator.js` using the overlays.
- Loads each collection's `collection.json` and optional `api.json`.
- Validates and deploys API functions/webhooks unless skipped.
- Syncs the assembled application config to PolyAPI.

Never expose `POLY_API_KEY` values. Do not rename PolyAPI functions casually;
old deployed functions are not cleaned up automatically. Variables referenced
in api/collection configs are not auto-deployed and require manual upload.
