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
| `webhooks/` | Public endpoint contracts, usually bound to their server function | `artifacts/webhooks/paybylink.json` |
| `triggers/` | Only when a direct binding is not enough: async, fan-out, or separately switchable wiring | `artifacts/triggers/paymentLinkTrigger.json` |
| `vari/` | Config, secrets, token caches, retry policies, error catalogs | `retryBackoff.json`, `errorCatalog.json`, `authorization.json` |
| `tabi/` | Persisted workflow state and lookup tables | `paymentEventCache.json` |
| `jobs/` | Scheduled cleanup or maintenance work | `prunePaymentEventCacheJob.json` |
| `canopy/` | Canopy UI definitions when the repo uses them | optional directory in each workflow |

## Alignment Rules

- If a webhook is public, keep one artifact per endpoint instead of a catch-all
  router artifact.
- When a webhook target changes, update its `serverFunction` binding (or its
  trigger, when one is used) in the same change.
- Keep context and function names aligned across:
  - the TypeScript entrypoint
  - inline `polyConfig` or function metadata JSON
  - webhook artifacts and their `serverFunction` reference
  - trigger artifacts, when used
- If the repo keeps generated schemas or ambient `schemas.*` types, treat them
  as the contract source of truth rather than inventing parallel interfaces.
- Some TypeScript repos use inline `polyConfig` in the `.ts` file instead of a
  separate function metadata JSON. Follow the active repo pattern instead of
  mixing both.

## Wiring a Webhook to Code

Bind the webhook to its server function by default:

```json
{
  "name": "paymentEvents",
  "context": "payments",
  "description": "Payment provider events.",
  "serverFunction": {
    "functionName": "routePaymentEvent",
    "functionContext": "payments"
  }
}
```

- Flow resolves `serverFunction` to the webhook's `serverFunctionId`; deploy the
  function first. `null` removes the binding; omitting the field leaves it
  unmanaged.
- The bound function receives `(eventPayload, headers, params)` like a
  trigger-invoked function, so its signature does not change.
- The call is synchronous: the function's response is the webhook's response,
  and the webhook's `responseStatus` still applies.
- The function must be in the webhook's environment, tenant-visible in the same
  tenant, or public. PolyAPI checks this on every call.
- A webhook serving several routes or event types usually binds one router
  function that dispatches by subpath or event type.

Use a trigger instead only when you need fire-and-forget handling
(`waitForResponse: false`), several functions reacting to one webhook, or wiring
you can enable or disable on its own. Never configure both: with a binding, the
webhook's triggers are skipped for calls in its own environment, so the trigger
silently stops firing. Webhook listeners are still notified. Error-handler
triggers (`source: errorHandler`) are unrelated to webhooks.

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
- Do webhook, function, and any trigger names still match?
- Is each webhook bound directly to its function, with a trigger only where a
  direct binding is not enough, and never both?
- Are `vari` and `tabi` being used for the right kind of data?
- Did the change update the right artifacts, not just the `.ts` file?
- Do tests cover the new contract or lifecycle behavior?
