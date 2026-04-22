# AGENTS.md

**PolyAPI-native serverless monorepo** with TypeScript functions + JSON artifacts (schemas, webhooks, triggers) synced to PolyAPI via CLI.

Docs: <https://docs.polyapi.io/platform_overview.html>

---

## Architecture

**PolyAPI Runtime:** Schemas → Webhooks → Triggers → Functions

**Flow:** Webhook receives request → validates against schema → trigger routes to function → function executes → response validated → returned

**Repo Structure:**

- `workflows/src/` — Function implementations by module (membersPbl, tokenOrchestration, utilities)
- `cli/` — Sync tool (schemas, webhooks, functions, triggers) + tests
- `designs/` — OpenAPI specs + JSON schemas (source of truth)

---

## Artifacts (The Contract)

PolyAPI requires JSON artifacts alongside TypeScript code:

**1. Schemas** — Input/output validation (`hookInput.json`, `hookOutput.json`)  
**2. Webhooks** — HTTP endpoint definitions (`paybylink.json`)  
**3. Functions** — Runtime code + metadata (`generatePayByLink.ts` + `.json`)  
**4. Triggers** — Route webhook → function (`paymentEventTrigger.json`)  
**5. Variables** — Runtime configuration and secrets (`apiKey.json` in `vari/`)

**Agent Task:** Update TS code + JSON artifacts + sync + test

---

## Naming Conventions

**Pattern:** `functionName.ts` + `functionName.json` + `webhookName.json` + `triggerName.json`

**Rules:**

- Keep names consistent across files
- Reuse shared schemas (no duplication)
- New workflows go under `workflows/src/` as a new module

---

## Environment

- **Package Manager:** `pnpm workspaces`
- **SDK:** `polyapi@0.25.9` (do not upgrade casually)
- **Secrets:** Never commit; use `.env` (validated early)
- **Namespace:** All artifacts must be namespaced via `POLYAPI_NAMESPACE` environment variable (e.g., "maybourne")

**Required Environment Variables:**

```env
POLYAPI_NAMESPACE=maybourne  # REQUIRED - enforced on all artifacts
BASE_URL=https://eu1.polyapi.io
API_KEY=your-api-key-here
```

**Namespace Enforcement:**

- All schemas, webhooks, functions, and triggers must have a `context` field
- Context must start with the namespace (e.g., `maybourne.members.pbl`)
- Validation happens during CLI sync - invalid namespaces are rejected
- This ensures all artifacts remain properly organized within the tenant

---

## Workflow

**1. Install:** `pnpm install`

**2. Edit Locally:**

- TypeScript functions (`workflows/src/**/*.ts`)
- JSON artifacts (`*.json`)
- Schemas (`designs/**` or module-local)

**3. Sync:** `pnpm run sync` or `pnpm --filter cli <sync-command>`

**4. Test:**

```bash
pnpm --filter workflows test        # Fast unit tests
pnpm --filter workflows test:e2e    # End-to-end integration tests (requires live environment)
pnpm --filter workflows test:all    # Unit + e2e sequentially
pnpm --filter workflows test src/tokenOrchestration/server/routePaymentEvent.test.ts # Specific test file
pnpm --filter workflows test src/tokenOrchestration/server/routePaymentEvent.test.ts --match 'throws POLY-MHG-1148 when merchantReference does not match stored payment context reference' # Specific test
```

---

## Adding a New Workflow

**Checklist:**

1. ✓ Create schemas (request + response)
2. ✓ Add `functionName.ts` implementation
3. ✓ Add `functionName.json` metadata
4. ✓ Add `webhookName.json` definition
5. ✓ Add `triggerName.json` mapping
6. ✓ Run sync
7. ✓ Test webhook (valid + invalid payloads)
8. ✓ Verify no secrets committed

**Implementation Rules:**

- Match schemas exactly (inputs/outputs)
- Validate early, fail fast
- Deterministic behaviour
- Log for debugging (never log secrets)

---

## Updating Workflows Safely

**Schema Changes:**

- ⚠️ Breaking changes affect callers immediately
- ✓ Additive only (new optional fields)
- ✓ Keep old fields unless deprecated
- ✓ Breaking changes → create v2

**Artifact Alignment:**

- TS code changed? → Check `.json` metadata, webhook schema refs, trigger mappings
- `tokenOrchestration` changed? → Review and update `workflows/src/tokenOrchestration/OVERVIEW.md`

**Quality Expectations:**

- Small, reviewable commits
- Strongly typed
- Schema-driven
- Testable
- No secrets in repo

---

## Troubleshooting

| Issue                    | Cause                                          | Fix                                                   |
| ------------------------ | ---------------------------------------------- | ----------------------------------------------------- |
| Webhook fails validation | Schema does not match payload                  | Update schema or client, do not loosen schema blindly |
| Invalid function output  | Output does not match schema                   | Match schema exactly and handle undefined fields      |
| Trigger does not fire    | Wrong webhook or function name, or sync failed | Verify JSON references and re run sync                |
| Sync creates duplicates  | Renamed artefacts without cleanup              | Follow naming patterns and update instead of create   |

---

## Rules for AI Agents

**DO NOT:**

- ❌ Commit secrets
- ❌ Loosen schemas to "make it work"
- ❌ Break contracts without versioning
- ❌ Add workflows without full artifact set
- ❌ Upgrade SDK versions casually
- ❌ Create documentation files unless explicitly requested

**ALWAYS:**

- ✓ Keep artifacts aligned with TS code
- ✓ Test after sync
- ✓ Validate JSON syntax
- ✓ Prioritize deterministic outputs
- ✓ Handle errors explicitly
- ✓ Put documentation in code comments or test files

## General Coding Guidelines

### Poly Usage Rules (Client and Server)

1) Call poly functions directly (no indirection)
Do not use `Reflect.get`, string-based property access, computed method names, or method extraction for any `poly.*` function (client or server).

Avoid:
const fn = Reflect.get(poly.some.domain.client, 'method');
await fn(input);

Avoid:
const method = poly.some.domain.client.method;
await method(input);

Required:
await poly.some.domain.client.method(input);

2) Do not re-cast poly functions locally
Do not use `as unknown as { ... }` to redefine or narrow the shape of `poly.*` functions if they are already typed.

3) Do not shadow poly namespaces
Avoid creating local variables such as:
const client = poly.some.domain.client;

unless:
- The poly namespace is untyped or incorrectly typed, or
- The variable materially improves readability in a very large function.

4) Preserve platform typings
Never override, narrow, or redefine existing `poly.*` typings unless absolutely necessary. Platform types are the source of truth.

5) Poly calls are boundary calls
Any call to `poly.*` (client or server) is considered an external boundary and is not subject to internal refactoring rules around helper depth or abstraction.

### Structure Rule – Keep the Main Function Readable

1) One main function per .ts file
Each `.ts` file must expose a single main client or server function. This function represents the primary logic flow and must remain easy to read from top to bottom.

2) Keep helper depth shallow
- Acceptable: `main()` → `helper()`
- Avoid: `main()` → `helper()` → `helper()` (and deeper)

3) When a 3rd level is allowed
A third level is only acceptable when it prevents meaningful duplication across multiple helpers, such as shared parsing, validation, mapping, or error handling.

4) Prefer explicit data passing over chained getters
Avoid patterns where helper A calls helper B which calls helper C to obtain data from the same root object. Extract once in `main()` (or one helper), then pass required values explicitly.

5) Read config and secrets close to use
Read variables and secrets in the function that performs the operation, assign them to local constants, and continue. Do not create helpers whose only purpose is reading or injecting configuration.

6) Avoid normalisation unless required
Do not normalise values unless required by a documented contract, failing tests, or observed production behaviour. If unsure, ask for verification.

7) Do not modify values from vari

Do not trim, normalise, or transform values read from `vari.*`. Treat them as trusted configuration and use them as provided.

### Type Rules – Keep Types Simple and Direct

1) Use `schemas.*` directly
If a type can reference `schemas.*` directly for a variable, parameter, or return type, do not create a new alias.

2) Avoid alias chains
Do not create multiple `type X = schemas.*` layers that simply rename schema types.

3) Only create a custom type when it adds value
A custom `type` is allowed only if:
- It represents a real domain concept, or
- It is reused in multiple places, or
- It removes repeated complex `NonNullable` or indexed access used in several functions.

4) Do not alias schema types just to shorten names
If the alias only shortens the name and adds no meaning, do not create it.

5) Keep poly typings local
If typing is required for a `poly.*` call, keep it local to the file. Do not create shared client types unless reused across files.

6) Do not create types when inference or schemas.* is sufficient

If a type can be inferred from a `poly.*` or `vari.*` call, or referenced directly via `schemas.*`, do not create a new `type`. Only introduce new types when they add real domain value or are reused.

### Defensive Coding Rule – No “Just In Case” Complexity

1) Do not add defensive code for guaranteed contracts
If a value is guaranteed by contract, schema, or platform behaviour, do not add extra null checks, try/catch blocks, fallbacks, or guards “just in case”.

2) Prefer the simplest correct implementation
Write the simplest code that satisfies the known contract. Avoid additional branches, defaults, or safety wrappers unless there is a real risk.

3) Add protection only for real boundaries
Defensive code is allowed only when:
- The value comes from an external or untrusted boundary, or
- There is known instability or historical failure, or
- The impact of failure is significant.

4) Avoid speculative resilience
Do not add complexity to protect against hypothetical scenarios that are not supported by evidence or contract.

5) Centralise unavoidable defensive logic
If defensive handling is required, implement it once in a shared utility rather than duplicating protective patterns across multiple files.

### JSON Field Access Rule – Deterministic Only

1) Read JSON values from explicit schema paths
Use fixed keys that map directly to the contract (for example: `metadata.customerId`, `opi.transToken`, `shopperLocale`).

2) Do not use catch-all key probing
Do not implement or use helpers that try multiple possible keys for the same value (for example fallback arrays like `readAdditionalDataValue(...)`).

3) If the source path changes, update the contract
When value location changes, update the schema/artifact and then update code to the new explicit path.

### Error Code Guidelines – Meaningful Tracking

Error codes identify failure points for support investigation and error handler routing. Use a **centralized catalog** and **unique codes** (not ranges).

**1. Maintain a code catalog, not ranges**
Do NOT assign code ranges by module (e.g., 1000-1999 for PBL). All codes are registered in the **error catalog vari** (`workflows/src/utilities/artifacts/vari/config/errorCatalog.json`), which is the single source of truth for code meanings and alert routing; the catalog entries are loaded at runtime by `errorAlerts.ts`.

**Example entry:**
```json
{
  "POLY-MHG-1024": {
    "action": "CORRECTIVE_ACTION",
    "description": "No profile found in Maybourne API for this customer at this point in the flow.",
    "maybourneGuidance": "In the Maybourne CRM, verify the customer profile exists for the customerId shown in this alert. If the profile is missing, investigate how the Pay By Link was created for an unrecognised customer. If the profile exists but was not returned (e.g. a transient API issue), contact the Maybourne API team.",
    "polyApiGuidance": "Once the profile issue is resolved, re-trigger the event via the function execution UI."
  }
}
```

**To add or update an error code:**
1. Edit `workflows/src/utilities/artifacts/vari/config/errorCatalog.json`
2. Add or modify the entry (see structure below)

Each entry has:
- **`action`**: one of `NO_SUPPORT_TEAM_ACTION` | `INVESTIGATION` | `CORRECTIVE_ACTION`
- **`description`**: a concise factual statement of the error state — what went wrong, not what to do about it. Do not include remediation guidance or investigative direction here.
- **`maybourneGuidance`**: guidance for the Maybourne support team. Do not include the "Maybourne team:" prefix — it is added at render time by `buildAlertGuidance`.
- **`polyApiGuidance`**: guidance for the Poly API support team. Do not include the "Poly API support:" prefix — it is added at render time.

**Action types:**
- `NO_SUPPORT_TEAM_ACTION` — expected/benign; Slack alert suppressed entirely. Use this **only** when the error is 100% the caller's fault (invalid or missing input they must correct and resubmit). Do not use for errors caused by our own code, payload construction, or configuration — even if a 4xx is returned to the caller.
- `INVESTIGATION` — something unexpected occurred that requires investigation. Use this when the failure originates in our code, config, or a third-party system (e.g., Adyen rejecting a payload we constructed, auth failures, API unavailability).
- `CORRECTIVE_ACTION` — a state change that partially or fully failed; manual data reconciliation is required (e.g., an OHIP profile was not created, a charge was not posted).

**Audience guidance:**

Alerts are sent to both the Maybourne support team (who have access to Opera Cloud and the Maybourne CRM, but not the Poly API platform) and the Poly API support team (who have access to execution logs, vari config, and the function execution UI). The Maybourne team is first-line — they follow the alert and escalate to Poly API support where needed.

Use `maybourneGuidance` and/or `polyApiGuidance` as appropriate. The `buildAlertGuidance` function prefixes each field with the correct audience label at render time:

```typescript
// Both teams need to act (most CORRECTIVE_ACTION entries)
maybourneGuidance: 'In Opera Cloud, navigate to Client Relations → Manage Profiles. ' +
  "Search for the guest using the customerId from this alert's context...",
polyApiGuidance: 'Confirm whether financial posting for this instance also needs to be verified.',

// Poly API action only — Maybourne team prompted to escalate
maybourneGuidance: 'Contact the Poly API support team, sharing the error details and context from this alert ' +
  '— a configuration fix may be required before this event can be re-processed.',
polyApiGuidance: 'Add the missing enterprise code mapping to the enterprises configuration ' +
  "(enterprise code visible in this alert's context), then re-trigger the event via the function execution UI.",

// Maybourne action only — no Poly API involvement needed
maybourneGuidance: 'In Opera Cloud, navigate to Client Relations → Manage Profiles → New Profile. ' +
  'Create the guest profile using the current member data from the Maybourne CRM.',
```

**2. Use same ID for log + single throw**
When a condition immediately produces one error:

```typescript
if (!input.amount) {
  poly.maybourne.utilities.log('error', ..., 'POLY-MHG-1001: missing amount');
  throw new HttpError(400, 'MISSING_AMOUNT', 'POLY-MHG-1001: ...');
}
```

**3. Use different IDs for log + branching throws**
When one log entry precedes multiple conditional throws, assign separate codes:

```typescript
// Log: describes the upstream failure point (diagnostic context)
poly.maybourne.utilities.log('error', ..., 'POLY-MHG-1013: Adyen call failed', { status, error });

// Throws: classify the specific failure type for handler routing
if (errorStatus === 401 || errorStatus === 403) {
  throw new HttpError(..., 'POLY-MHG-1014: ...');  // Different code
}
if (errorStatus === 400 || errorStatus === 422) {
  throw new HttpError(..., 'POLY-MHG-1015: ...');  // Different code
}
throw new HttpError(..., 'POLY-MHG-1016: ...');    // Different code
```

Why? The error handler sees the thrown exception code, not the log code. Unique throw codes let the handler and support team understand **which specific failure path was taken**.

**4. Keep codes unique and searchable**
- Never reuse a code for multiple unrelated errors
- Keep codes in the error message text (e.g., `'POLY-MHG-1001: ...'`) — the error handler extracts the code from the message string via regex, so the `POLY-MHG-####` prefix must appear at the start of the message
- Make codes greppable: future changes can easily find all references

**5. Register new codes in the error catalog vari**
When adding a new error code, edit `workflows/src/utilities/artifacts/vari/config/errorCatalog.json` and add an entry:

**For `INVESTIGATION` entries** (unexpected failures requiring investigation):
```json
"POLY-MHG-1XXX": {
  "action": "INVESTIGATION",
  "description": "Adyen service error (5xx) on paymentLinks.create.",
  "maybourneGuidance": "Check https://status.adyen.com for active incidents. Contact the Poly API support team, sharing the error details and context from this alert, to re-attempt once the service is restored.",
  "polyApiGuidance": "Check https://status.adyen.com and re-attempt via the function execution UI once the service is restored."
}
```

**For `CORRECTIVE_ACTION` entries** (state changes requiring manual reconciliation):
```json
"POLY-MHG-1YYY": {
  "action": "CORRECTIVE_ACTION",
  "description": "OHIP profile create failed — profile was not created.",
  "maybourneGuidance": "In Opera Cloud, navigate to Client Relations → Manage Profiles → New Profile. Create the guest profile using the current member data from the Maybourne CRM.",
  "polyApiGuidance": "Confirm whether financial posting for this instance also needs to be verified."
}
```

**For `NO_SUPPORT_TEAM_ACTION` entries** (expected/benign — caller fault only):
```json
"POLY-MHG-1ZZZ": {
  "action": "NO_SUPPORT_TEAM_ACTION",
  "description": "Payment event was unsuccessful — orchestration skipped."
}
```

**Do NOT:**
- ❌ Assign error code ranges by module or function
- ❌ Reuse the same code (unless specifically for tightly related log/error pairs)
- ❌ Log an error without including its code in the message
- ❌ Add a new error code without updating the vari catalog (`workflows/src/utilities/artifacts/vari/config/errorCatalog.json`)
- ❌ Leave `maybourneGuidance` or `polyApiGuidance` absent on `INVESTIGATION` or `CORRECTIVE_ACTION` entries
- ❌ Include the "Maybourne team:" or "Poly API support:" prefix in guidance field values — these are added at render time
- ❌ Include investigative direction or remediation guidance in `description` — keep it factual
