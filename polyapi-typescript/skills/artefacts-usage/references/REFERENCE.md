# TypeScript Artifact Reference

## Typical Workflow Layout

Maybourne-style TypeScript PolyAPI repos are organized by workflow:

```text
src/
  <workflow>/
    artifacts/
      canopy/
      jobs/
      schemas/
      specs/
      tabi/
      triggers/
      vari/
      webhooks/
    client/
    server/
    types/
  utilities/
    artifacts/
    client/
    server/
    types/
```

Keep the runtime code, artifacts, and tests for one workflow close together.
Put shared helpers under `src/utilities/` only when they are reused across
workflows.

## Authoritative schema source

Use `https://eu1.polyapi.io/swagger-json` as the source of truth for the JSON
body shape of platform-managed artefacts. The checked-in repo conventions tell
you where files live and how names align; the swagger tells you which fields
the platform accepts.

| Folder | Swagger resource | Create DTO |
| --- | --- | --- |
| `webhooks/` | `/webhooks` | `CreateWebhookHandleDto` |
| `triggers/` | `/triggers` | `CreateTriggerDto` |
| `vari/` | `/variables` | `CreateVariableDto` |
| `schemas/` | `/schemas` | `CreateSchemaDto` |
| `jobs/` | `/jobs` | `CreateJobDto` |
| `tabi/` | `/tables` | `CreateTableDto` |

Notes:

- The platform API names the `tabi` resource `tables`.
- `canopy/` is not exposed under the same name in `swagger-json`; follow
  checked-in repo examples or separate Canopy guidance for that artefact type.

## Artifact Types

| Artifact | Purpose | Maybourne-style example |
| --- | --- | --- |
| `schemas/` | Payload contracts shared by webhooks, triggers, or generated types | request and response schemas for pay-by-link and payment events |
| `specs/` | Upstream provider specs or OpenAPI-derived sources | external API specs checked in near the workflow |
| `webhooks/` | Public endpoint contracts | `artifacts/webhooks/paybylink.json` |
| `triggers/` | Route a webhook to the target function | `artifacts/triggers/paymentLinkTrigger.json` |
| `vari/` | Config, secrets, token caches, retry policies, error catalogs | `retryBackoff.json`, `errorCatalog.json`, `authorization.json` |
| `tabi/` | Persisted workflow state and lookup tables | `paymentEventCache.json` |
| `jobs/` | Scheduled cleanup or maintenance work | `prunePaymentEventCacheJob.json` |
| `canopy/` | Canopy UI definitions when the repo uses them | optional directory in each workflow |

## Alignment Rules

- If a webhook is public, keep one artifact per endpoint instead of a catch-all
  router artifact.
- When a webhook target changes, update the paired trigger in the same change.
- Keep context and function names aligned across:
  - the TypeScript entrypoint
  - inline `polyConfig` or function metadata JSON
  - webhook artifacts
  - trigger artifacts
- If the repo keeps generated schemas or ambient `schemas.*` types, treat them
  as the contract source of truth rather than inventing parallel interfaces.
- Some TypeScript repos use inline `polyConfig` in the `.ts` file instead of a
  separate function metadata JSON. Follow the active repo pattern instead of
  mixing both.

## Choosing Between `vari`, `tabi`, and `jobs`

- Use `vari` when the data is configuration, a secret, a retry/backoff policy,
  or a cached token/value that the runtime reads as configuration.
- Use `tabi` when the data is workflow state or lookup data that must persist
  across separate executions and be queried later.
- Use `jobs` when stale `tabi` records or lifecycle state need scheduled
  cleanup.

Maybourne’s `paymentEventCache` pattern is the clearest example:

- `generatePayByLink` writes routing context to `tabi`
- `routePaymentEvent` reads it back during webhook handling
- `prunePaymentEventCacheJob` cleans up old rows on a schedule

## Review Checklist

- Does the workflow still have a coherent `src/<workflow>/` shape?
- Do webhook, trigger, and function names still match?
- Are `vari` and `tabi` being used for the right kind of data?
- Did the change update the right artifacts, not just the `.ts` file?
- Do tests cover the new contract or lifecycle behavior?
