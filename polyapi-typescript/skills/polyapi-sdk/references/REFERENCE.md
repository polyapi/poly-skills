# TypeScript PolyAPI SDK Reference

## Toolchain Discovery Checklist

Before changing runtime code or deployment flow, inspect the active repo for:

- package manager and lockfile (`pnpm`, `npm`, `yarn`)
- build scripts
- sync or push scripts
- how function metadata is declared
- existing `polyapi` dependency version
- neighboring tests that prove the expected calling pattern

In a typical PolyAPI TypeScript workspace, those signals come from
`package.json`, workflow structure under `src/` or `workflows/src/`, and
neighboring `*.test.ts` files.

## Imports

Use direct imports from `polyapi`:

```typescript
import poly, {
  type PolyClientFunction,
  type PolyServerFunction,
  polyCustom,
  tabi,
  vari,
} from 'polyapi';
```

Only import the helpers you actually use, but keep them sourced from
`polyapi` directly.

## Function Metadata

Many TypeScript PolyAPI repos keep function metadata inline:

```typescript
const polyConfig: PolyServerFunction = {
  name: 'routePaymentEvent',
  context: 'platform.payments.orchestration',
  description: 'Routes incoming payment events to the correct handler',
};
```

Keep this aligned with the deployed function name and context used by matching
trigger artifacts.

Other repos may use separate function metadata JSON instead. Follow the active
repo pattern; do not mix patterns inside one codebase unless the repo already
does.

## Entrypoint Shape

Server and client entrypoints should usually be a single default async export
typed with the generated contract:

```typescript
export default async function routePaymentEvent(
  input: schemas.Platform.Payments.WebhookInput
): Promise<schemas.Platform.Payments.WebhookOutput> {
  // ...
}
```

Prefer generated `schemas.*` and `tabi.*` types directly when they already
represent the real platform contract.

## Status Handling

At webhook boundaries, some repos set HTTP status explicitly:

```typescript
polyCustom.responseStatusCode = 400;
```

Only do this at the boundary handler that owns the HTTP response semantics.
Do not scatter status mutation through internal helpers.

## Build, Sync, and Test Loop

Use the repo’s existing command path instead of inventing a new one.

For example, a workspace-managed repo might expose scripts like:

```bash
pnpm install
pnpm --filter workflows test
pnpm --filter cli run build && cli push
```

Treat those as repo-specific examples, not global defaults. The reusable rule
is:

1. Discover the existing build and sync path from the repo.
2. Run it after TypeScript or artifact changes.
3. Run the nearest targeted tests before finishing.

## Review Checklist

- Are imports coming directly from `polyapi`?
- Are `poly.*` and `vari.*` references called through generated namespaces
  directly, without `as unknown as` casts or local platform aliases?
- Does the entrypoint use generated platform types where available?
- Does metadata stay aligned with deployed context and trigger wiring?
- Did the change follow the repo’s existing build or sync path?
- Was the pinned `polyapi` version treated as an intentional dependency?
