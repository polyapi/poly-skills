---
name: polyapi-runtime-testing
description: Use when writing, reviewing, or debugging PolyAPI TypeScript tests that invoke deployed functions, depend on generated SDK paths, need server-function log verification, or may mutate external systems.
---

# PolyAPI Runtime Testing

## Overview

PolyAPI integration tests prove deployed runtime behavior. Local unit tests prove
branch logic. Keep both layers explicit so passing mocks are not mistaken for a
working platform deployment.

## Quick Reference

- Keep mocked unit tests in `*.test.ts`.
- Put deployed-function tests in `*.integration.test.ts`.
- Call deployed functions through generated `poly.*` SDK paths.
- Do not import server/client implementation files in integration tests.
- Refuse `prod.env` by default in integration tests.
- Gate mutating integration tests behind an explicit env flag.
- Use server-function logs during development to verify runtime behavior.
- Do not bake log scraping into test assertions unless the repo explicitly
  chooses that pattern.

## Test Layers

| Layer | Purpose | Calls |
| --- | --- | --- |
| Unit | Fast branch and error-path coverage | Local imports with mocked `polyapi` |
| Integration | Deployed function transport and platform state | Generated `poly.*` SDK |
| Mutating integration | Deployed behavior that changes external state | Generated `poly.*` SDK with explicit opt-in |

## Integration Test Rules

Use integration tests for deployed PolyAPI behavior:

```typescript
import poly from 'polyapi';
import test from 'ava';

test.serial('routeEvent deployed function accepts the deployed payload contract', async t => {
  const result = await poly.example.events.routeEvent(event, {});
  t.truthy(result);
});
```

Guard production by default:

```typescript
const envPath = process.env.ENVPATH || 'workflows/dev.env';
if (envPath.endsWith('prod.env')) {
  throw new Error('Refusing to run integration tests against prod.env.');
}
```

Gate external mutations:

```typescript
const RUN_MUTATING_INTEGRATION =
  process.env.RUN_MUTATING_INTEGRATION === 'true';

if (RUN_MUTATING_INTEGRATION) {
  test.serial('updates the external system', async () => {
    await poly.example.system.updateThing(input);
  });
} else {
  test.skip('updates the external system', async () => {});
}
```

Use project-specific aliases such as `RUN_ZOOM_MUTATION_INTEGRATION` only when
the narrower name is clearer for that repo.

## Platform-First Setup

When a test needs a new generated construct:

1. Create or update the artefact.
2. Ask for approval for the exact non-production deploy command.
3. Deploy the artefact to the approved environment.
4. Regenerate the SDK from the same environment.
5. Write the integration test against the generated path.

Do not use local `.d.ts` shims, `@ts-expect-error`, `as unknown as`, or untyped
SDK access to make tests compile before the platform state exists.

## Log Verification

During development, verify server-function behavior with the repo's log helper
or the PolyAPI logs API after invoking the deployed function.

- Server functions have standalone logs.
- Client function logs appear inside the calling server function execution.
- Passing integration tests may only prove the function returned; if the server
  function catches errors, inspect logs to verify the intended branch.
- Use traceable IDs or metadata in test payloads so logs are searchable.

## Command Shape

Prefer explicit scripts:

```json
{
  "scripts": {
    "test": "ava",
    "test:integration": "ava --config ava.config.integration.cjs",
    "test:integration:mutating": "RUN_MUTATING_INTEGRATION=true ava --config ava.config.integration.cjs"
  }
}
```

Adapt the runner only if the repo has an established different test runner, but
keep the default unit command non-mutating.

## Common Mistakes

- Replacing unit tests with integration tests instead of keeping both.
- Running mutating tests as part of the default `test` script.
- Calling local implementation files from integration tests.
- Assuming a passing integration test proves business behavior when the server
  function catches and logs errors.
- Forgetting to deploy and regenerate the SDK before referencing new platform
  paths.
