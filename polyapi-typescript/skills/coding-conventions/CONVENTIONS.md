# TypeScript Conventions

Concrete conventions for PolyAPI-oriented TypeScript codebases.

This file captures the detailed TypeScript conventions used by this repo's
PolyAPI skills. It is intentionally opinionated toward production PolyAPI
workflow and CLI patterns.

## Workspace Layout

Typical top-level structure:

```text
repo/
├── workflows/
└── cli/
```

- `workflows/` holds PolyAPI TypeScript implementations
- `cli/` holds artifact validation and sync tooling

Typical workflow layout:

```text
workflows/src/<integrationName>/
  OVERVIEW.md
  artifacts/
    schemas/
    webhooks/
    triggers/
    vari/
    jobs/
    tabi/
    canopy/
    specs/
  server/
    <functionName>.ts
    <functionName>.json
  client/
    <functionName>.ts
    <functionName>.json
```

- Shared code belongs under `workflows/src/utilities/`
- Keep server and client metadata JSON beside the `.ts` file with the same
  basename
- Keep webhook, trigger, variable, job, and table filenames internally
  consistent within the workflow

## Formatting

- Use Biome-style formatting: single quotes, semicolons, trailing commas,
  2-space indentation, and wrapped lines over wide one-liners
- Prefer `const`; use `let` only for genuine reassignment
- Use `import type` for type-only imports when it improves clarity
- Keep comments for intent, platform quirks, or non-obvious tradeoffs

```typescript
import poly, { vari } from 'polyapi';

const MAX_RETRIES = 3;
```

## File Shape

### One main function per file

- Each `.ts` file should have one primary exported function or utility
- The main path should read top-to-bottom without jumping through layers of
  helpers
- Small local helpers are fine when they remove real duplication

### Keep helper depth shallow

- Normal: `main()` -> `helper()`
- Avoid: `main()` -> `helper()` -> `helper()` -> `helper()`
- A third level is acceptable only for repeated parsing, mapping, or shared
  error handling
- Pass extracted values explicitly instead of having several helpers re-read the
  same root object

```typescript
// ✅ GOOD
export async function processEvent(input: EventInput): Promise<EventOutput> {
  const eventId = input.eventId;
  if (!eventId) {
    throw new Error('Missing eventId');
  }

  const event = await loadEvent(eventId);
  const context = buildContext(event);
  return dispatchEvent(event, context);
}

// ❌ BAD
export async function processEvent(input: EventInput): Promise<EventOutput> {
  return dispatch(loadAndValidateAndBuildContext(input));
}
```

## Platform Boundaries

### Call `poly.*` directly

Do not hide platform calls behind method extraction, `Reflect.get`, computed
property access, or unnecessary namespace aliases.

```typescript
// ✅ GOOD
await poly.platform.payments.capture(input);

// ❌ BAD
const capture = poly.platform.payments.capture;
await capture(input);

// ❌ BAD
const paymentsClient = poly.platform.payments;
await paymentsClient.capture(input);
```

### Do not re-cast platform APIs

- Do not use `as unknown as { ... }` or local compatibility aliases to
  redefine the shape of `poly.*` or `vari.*`
- Call generated `poly.*` functions and `vari.*` paths directly and
  deterministically
- If generated SDK typings are stale or a path does not exist, deploy the
  matching artefact to an approved non-production environment and run the
  repo's SDK generation path instead of papering over the mismatch with casts
- Only use local types for real input/output domain data, not to reshape
  platform namespaces

### Boundary rule

Treat these as external boundaries:

- `poly.*`
- `vari.*`
- `process.env`
- Filesystem access
- HTTP requests
- Webhook or JSON payloads

Boundary code may justify validation, logging, and explicit errors. Inner code
should stay simple.

## Types

### Use `schemas.*` directly when it already matches the contract

```typescript
// ✅ GOOD
export async function routePaymentEvent(
  input: schemas.Platform.Payments.WebhookInput
): Promise<schemas.Platform.Payments.WebhookOutput> {
  // ...
}

// ❌ BAD
type PaymentWebhookInput = schemas.Platform.Payments.WebhookInput;
type PaymentWebhookOutput = schemas.Platform.Payments.WebhookOutput;

export async function routePaymentEvent(
  input: PaymentWebhookInput
): Promise<PaymentWebhookOutput> {
  // ...
}
```

### Create custom types only when they add value

Add a local `type` only when it:

- Represents a real domain concept
- Is reused across multiple functions in the file
- Removes repeated complex indexing or `NonNullable` noise

### Prefer `unknown` to `any` at untrusted boundaries

```typescript
function getPaymentContextId(value: unknown): string | null {
  if (!value || typeof value !== 'object') {
    return null;
  }

  const record = value as Record<string, unknown>;
  return typeof record.paymentContextId === 'string'
    ? record.paymentContextId
    : null;
}
```

- `unknown` forces narrowing
- `Record<string, unknown>` is acceptable for raw object-like payloads
- Avoid `any` except inside tightly contained compatibility code

## JSON and Contract Access

- Read values from explicit, contract-backed paths
- Do not probe multiple fallback keys "just in case"
- If the source path changes, update the contract and then update the code

```typescript
const rawAdditionalData = notificationItem?.additionalData as
  | Record<string, unknown>
  | undefined;

const paymentContextId =
  typeof rawAdditionalData?.['metadata.paymentContextId'] === 'string'
    ? rawAdditionalData['metadata.paymentContextId']
    : null;
```

Prefer one explicit extraction over generic helpers that search several possible
keys.

## Config and Secrets

- Read `vari.*` close to the operation that uses it
- Do not create helpers whose only job is to fetch configuration
- Do not trim, normalise, or otherwise transform `vari.*` values unless a
  documented contract requires it
- Validate required `process.env` values early in CLI or startup code
- Never log secrets, raw credentials, or tokens

```typescript
async function postStatusUpdate(payload: StatusPayload): Promise<void> {
  const apiConfig = await vari.platform.payments.config.api.get();

  await poly.platform.http.post({
    baseUrl: apiConfig.baseUrl,
    body: payload,
  });
}
```

## Error Handling and Logging

- Fail fast with guard clauses for required input
- Catch `unknown`
- Log structured context with identifiers that help debug the failure
- Throw or return explicit errors after logging
- Never log secrets

```typescript
function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

try {
  await sendRequest(payload);
} catch (error: unknown) {
  poly.platform.utilities.log(
    'error',
    'sendRequest',
    'Failed to send request',
    {
      requestId,
      error: getErrorMessage(error),
    }
  );
  throw new Error(`Failed to send request for requestId=${requestId}`);
}
```

### Searchable error codes

If the repo uses an error code catalog:

- Keep codes unique and greppable
- Include the code in the logged or thrown message text
- Register new codes in the catalog in the same change
- Use different codes for diagnostic logs and specific thrown branches when they
  represent different failure points

## Async and Side Effects

- Keep dependent operations sequential
- Use `Promise.all` only for independent boundary calls
- Use `Promise.allSettled` when fan-out work should not block sibling work
- Prefer deterministic data shaping before I/O
- Do not hide side effects inside generic helpers with vague names

```typescript
const [retryBackoff, apiConfig] = await Promise.all([
  vari.platform.utilities.config.retryBackoff.get(),
  vari.platform.payments.config.api.get(),
]);
```

## Defensive Coding

- Do not add defensive branches for values guaranteed by schema, contract, or
  platform behaviour
- Prefer the simplest correct implementation
- Add protection only for real boundaries or known unstable behaviour
- Centralise unavoidable defensive logic instead of duplicating it across files

```typescript
// ✅ GOOD: guard untrusted input
if (!merchantReference) {
  throw new Error('Missing merchantReference');
}

// ❌ BAD: defensive noise on a trusted config shape
const logLevel =
  typeof config?.logLevel === 'string' ? config.logLevel.trim() : 'info';
```

## Artifacts and Contracts

- When TypeScript changes a contract, update the matching JSON artifacts, schema
  refs, triggers, or metadata in the same change
- Make schema changes additive by default
- Version breaking changes rather than silently mutating existing contracts
- Keep naming aligned across `.ts`, `.json`, webhook, and trigger files when the
  repo uses paired artifacts
- Use the live folder spellings: `artifacts/`, `vari/`, and `tabi/`
- Use `artifacts/`, not `artefacts/`

Example aligned set:

```text
workflows/src/payments/server/processPayment.ts
workflows/src/payments/server/processPayment.json
workflows/src/payments/artifacts/schemas/paymentInput.json
workflows/src/payments/artifacts/webhooks/paymentEvents.json
workflows/src/payments/artifacts/triggers/paymentEventsTrigger.json
```

## Tests

- Co-locate `*.test.ts` files with the behaviour they verify
- Use descriptive, behaviour-first names
- Create small builders or stubs for inputs and boundary dependencies
- Always restore mocks, globals, or environment changes with teardown/cleanup
- Test happy paths, contract violations, and boundary failures

```typescript
import test from 'ava';

test.serial('throws when merchantReference is missing', async t => {
  const input = buildInput({ merchantReference: null });

  const error = await t.throwsAsync(() => routePaymentEvent(input));

  t.is(error?.message, 'Missing merchantReference');
});
```

## Common Mistakes

- Hiding `poly.*` calls behind generic wrappers
- Aliasing `schemas.*` types just to shorten names
- Normalising trusted `vari.*` values without a contract reason
- Adding speculative resilience for hypothetical failures
- Updating TypeScript without aligned artifacts or tests
- Renaming or restructuring workflow files without keeping paired JSON metadata
  and artifact names consistent
