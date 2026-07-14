---
name: boomi-to-polyapi-conversion
description: Use when converting an already-analyzed Boomi integration into a PolyAPI TypeScript workflow and you need mandatory playback and approval gates before implementation.
---

# Skill: Dell Boomi to PolyAPI Conversion

Use this skill to convert an already-analyzed Boomi integration into a
deployable PolyAPI TypeScript workflow.

## When To Use

Load this skill before:

-   starting Stage 3 conversion after source download and compression
-   reviewing a completed migration for correctness
-   resuming an in-progress migration after context interruption

This skill orchestrates dependent skills. Keep rules in their source skills and
load them at the indicated stage.

## Boomi Migration Constraints

These constraints apply across every step of this skill, from analysis through
implementation:

-   Preserve Boomi-derived request and response payload shapes unless a
    contract change is explicitly approved.
-   Preserve Boomi-derived status codes and trigger styles unless explicitly
    approved.
-   Do not introduce response wrapper keys unless Boomi payloads already
    include those wrapper keys.
-   For secret variables, keep identity and secrecy metadata only; never
    commit secret values.

## Step 1 - Mandatory Input Gate

Required inputs:

-   integration name (mandatory)
-   approved target PolyAPI design (mandatory, ideally diagram plus notes)

If integration name is missing, ask exactly:

`What is the name of the Boomi integration you want to migrate?`

The integration name is missing unless the active user request explicitly names
the integration to migrate or the user answers this prompt. Do not infer the
integration from open IDE tabs, active files, manifest filenames, folder names,
previous analysis context, or likely repository state.

When invoked without an explicit integration name in the active request, ask
only the integration-name question and stop. Do not ask for the approved design
in the same response.

After the integration is provided, if the approved design is missing, ask
exactly:

`Please provide the approved target PolyAPI design, ideally as a diagram plus any supporting notes.`

If the user response contains only an integration name or integration path, the
approved design is still missing. Ask the design question and stop. Do not run
preflight, inspect source, or produce playback.

If the design is not provided, stop and wait.

Until both inputs are available, do not inspect Boomi source files, read analysis
manifests, analyze repository conventions, infer architecture, propose an
implementation plan, or generate code. The only allowed behavior is requesting
the missing input and waiting.

## Step 2 - Preflight Evidence

After both required inputs are available, run preflight checks under
`boomi-integrations/<integrationName>/`:

-   `raw/<name>.componentMetadata.xml`
-   `raw/<name>.component.xml`
-   `raw/<name>.componentGraph.json`
-   `analysis/compactEvidence.json`
-   `analysis/compactEvidence.md`

If preflight files are missing, stop and return a concise file plan. Instruct the
user to run Stage 1 and Stage 2 prompts first:

-   `/boomi-download-source <integrationName>`
-   `/boomi-compress-source <integrationName>`

## Step 3 - Design and Source-Derived Construct Analysis

Before playback, load planning skills:

-   `polyapi-common/skills/design-analysis/SKILL.md`
-   `polyapi-common/skills/polyapi-constructs/SKILL.md`
-   `polyapi-typescript/skills/artefacts-usage/SKILL.md`
-   `boomi-to-polyapi/skills/naming-conventions-boomi/SKILL.md`
-   `boomi-to-polyapi/skills/generate-schemas-boomi/SKILL.md`

Use `design-analysis` to interpret the approved design diagram and notes
before source-derived planning. Compare design intent against confirmed Boomi
behavior and classify gaps as high-level design omissions, likely design
mistakes, or intentional behavior changes requiring confirmation.

Analyze the Boomi evidence and current repository patterns. Derive, do not ask
the user to provide:

-   PolyAPI construct mapping for each Boomi entrypoint, process, subprocess,
    map, script, connector, property, schedule, and stateful behavior
-   boundary payload format handling for each public request, response, and
    downstream call, including whether XML, SOAP, CSV, fixed-width, or JSON is
    parsed/decoded or serialized/encoded at the boundary
-   Boomi Map Editor transformation handling separately from boundary payload
    format conversion, including source profile, target profile, map functions,
    constants, defaults, lookups, and occurrence behavior
-   secret, obscured, and non-secret runtime variables
-   variable artifact names, contexts, descriptions, secrecy, visibility, and
    TypeScript usage
-   jobs, tables, schemas, webhooks, triggers, server functions, client
    functions, and shared utilities
-   downstream systems, side effects, and adapter needs
-   third-party SDK package requirements implied by the implementation
-   IBM i RPG programs called via JT400 or `db2Adapter` that require one-time stored procedure registration before first use (see RPG Detection rules below)

Use `POLYAPI_CODEAGENT.md` as the implementation guide for Boomi source recovery
and PolyAPI construct mapping.

### IBM i RPG Program Detection

Scan all Boomi source and dependency XML files for RPG programs that will be
called via `db2Adapter` procedure mode. These programs exist as compiled RPG
objects on the IBM i and must be registered as SQL stored procedures before
`db2Adapter` (ODBC) can call them. Registration is a one-time DBA step that
happens outside the PolyAPI deployment.

**Detection signals — check for any of the following in the Boomi source:**

1. A `dataprocess` shape containing a Groovy script that imports
   `com.ibm.as400.access.*` and calls `ProgramCall` or `pgm.run()`
2. A dynamic process property named `AS400 Full Program Name` populated via a
   cross-reference lookup (e.g. table `RPG Programs - Middleware`)
3. A connector action using connection type `rpgsp` or an HTTP connector with
   a base URL pointing to a known RPGsp server

**Extraction — for each detected RPG call, derive:**

| Signal                               | What to extract                                                                                                                                 |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Program path (from cross-ref or DPP) | Format `/QSYS.LIB/<LIBRARY>.LIB/<PROGRAM>.PGM`                                                                                                  |
| Library name                         | Middle segment of the path, e.g. `PRD1FHMODP`                                                                                                   |
| Program name                         | Final segment without `.PGM`, e.g. `OI491`                                                                                                      |
| INOUT parameter size                 | From the `padRight(N, " ")` or equivalent padding step that prepares the flat-file input; this becomes `CHAR(N)`                                |
| Parameter direction                  | Always `INOUT` when the same buffer carries both input and output; use `IN`/`OUT` only when Boomi evidence shows separate send/receive profiles |

**Generated DDL — produce one block per detected RPG program:**

```sql
-- Check whether already registered:
SELECT SPECIFIC_SCHEMA, SPECIFIC_NAME, ROUTINE_TYPE
FROM QSYS2.SYSROUTINES
WHERE SPECIFIC_NAME = '<PROGRAM>' AND SPECIFIC_SCHEMA = '<LIBRARY>'

-- Register (run once, requires CREATE authority in <LIBRARY>):
CREATE OR REPLACE PROCEDURE <LIBRARY>.<PROGRAM> (
  INOUT RPGPARAM CHAR(<N>)
)
LANGUAGE RPGLE
NOT DETERMINISTIC
EXTERNAL NAME '<LIBRARY>/<PROGRAM>'
PARAMETER STYLE GENERAL
```

Replace `<LIBRARY>`, `<PROGRAM>`, and `<N>` with the extracted values.
A successful DDL execution returns `rowCount: 0` with no error.

Include this DDL in the **Implementation Plan playback** under a dedicated
`IBM i Prerequisites` section and in the generated `OVERVIEW.md` under a
`## IBM i Prerequisite` heading so the operator can execute it before the first
deployment.

Variable and package rules:

-   Create required `vari` artifacts automatically from Boomi evidence and
    planned source code.
-   For secrets and obscured values, create identity and secrecy metadata only;
    never ask for, invent, read, or store secret values.
-   Treat process properties and environment extensions as non-secret variables
    unless Boomi evidence shows credential or sensitive usage.
-   Treat connection passwords, API keys, tokens, and credentials as secret or
    obscured variables based on repository and platform conventions.
-   Include proposed package/dependency changes in playback and wait for
    explicit approval before changing dependency files.
-   Stop for a targeted clarification only when Boomi evidence proves a
    dependency exists but does not provide enough information to safely name,
    classify, or scope it.

## Step 4 - Clarifications and Implementation Plan Playback

Do not write code until playback is approved.

Playback must include these named sections in order:

1. `Clarifications Needed`
2. `Assumptions`
3. `Behavioural Risk Detection`
4. `IBM i Prerequisites` — list every RPG program detected in Step 3; include the generated registration DDL for each; mark `None` if no RPG programs were detected
5. `Implementation Plan`

`Clarifications Needed` must ask direct questions required to remove ambiguity.
If any question changes the public contract, payload shape, status code, target
construct, downstream side effect, credential/variable classification,
dependency change, or approved design interpretation, stop after the questions
and wait for answers. Do not run the implementation approval gate yet. If there
are no blocking clarifications, state `None`.

`Assumptions` must list every assumption and inferred behavior. Label each item
as confirmed from target design, confirmed from Boomi source evidence, or
inferred by the agent.

`Behavioural Risk Detection` must list source/design mismatches. For each risk,
explain the Boomi behavior, what in the design might break or omit it, whether
it looks like a design mistake/high-level omission/intentional change, and the
proposed correction.

`Implementation Plan` must include the mandatory implementation checklist from
`POLYAPI_CODEAGENT.md`, with the following Stage 3 detail:

1. Scope summary
2. Approved design interpretation
3. Input contract (trigger, method, path, request shape)
4. Output contract (all statuses and payload branches)
5. Boundary payload format plan for each inbound, outbound, and downstream
   payload, including where non-JSON formats are parsed/decoded and
   serialized/encoded
6. Boomi Map Editor transformation logic in order, separately from boundary
   format conversion
7. Dependencies (systems, variables, side effects)
8. Workflow name and file plan under `workflows/src/<integrationName>/`
9. Webhooks, triggers, server functions, client functions, utilities/adapters,
   variables, secrets, `tabi` tables, jobs, downstream integrations, schema sources,
   XML/JSON handling, status-code parity, tests, and reuse of existing patterns
10. PolyAPI construct mapping from Boomi source constructs to proposed artifacts
    and functions

Include a payload parity checkpoint:

-   Boomi runtime payload example vs proposed PolyAPI payload example
-   request and response body parity for success and error branches
-   boundary format parity, including XML attributes/elements, repeated nodes,
    namespaces, empty values, and string preservation where applicable
-   no added wrapper keys unless Boomi includes those keys

Include a Boomi Map Editor parity checkpoint:

-   source profile and target profile for each material Boomi map
-   source paths, target paths, constants, defaults, functions, cross-reference
    lookups, occurrence behavior, and conditional mapping rules
-   whether each map becomes a client function, shared utility, or local helper,
    with the reason
-   explicit confirmation that boundary XML/JSON conversion is not being treated
    as the same thing as Boomi Map Editor transformation logic

Include a source-derived runtime variable contract:

-   group variables by secret, obscured, and non-secret
-   map each variable to Boomi evidence, TypeScript usage, artifact file, and
    downstream dependency
-   identify metadata-only variables whose values must be set outside source
    control
-   explain any ambiguous variable naming or secrecy classification requiring
    explicit approval

Include a source-derived dependency contract:

-   list third-party SDK packages that the implementation requires
-   explain why each package is needed and which code will import it
-   identify dependency-file changes that require explicit approval

Only run the implementation approval gate after blocking clarifications are
answered or when `Clarifications Needed` is `None`.

After playback, run this exact implementation approval gate:

1. `Implementation is paused at the mandatory approval gate.`
2. `Reply with explicit approval to proceed.`
3. `Approve yes/no:`

Implementation approval authorizes code and artifact edits only. It does not
authorize deployment. Each `pnpm workflows push` still requires the separate
Step 8 deployment approval gate.

Branching rules:

-   If user answers `yes`, continue to Step 5.
-   If user answers `no`, do not implement. Ask exactly: `What should be changed before implementation?`
-   Update playback with requested changes and ask the same implementation approval gate again.

## Step 5 - Implement TypeScript and Artifacts

Load shared implementation skills before writing files:

-   `polyapi-typescript/skills/coding-conventions/SKILL.md`
-   `polyapi-typescript/skills/coding-standards/SKILL.md`
-   `polyapi-typescript/skills/artefacts-usage/SKILL.md`
-   `boomi-to-polyapi/skills/generate-schemas-boomi/SKILL.md`
-   `boomi-to-polyapi/skills/naming-conventions-boomi/SKILL.md`
-   `polyapi-common/skills/polyapi-constructs/SKILL.md`

Preserve exact Boomi behavior unless a change is explicitly approved.

Keep webhook, trigger, schema, and function artifacts aligned with implemented
TypeScript behavior and the Boomi boundary contract.

Create derived `vari` artifacts during implementation when runtime code or Boomi
evidence requires them. Keep secret values out of source files.

When TypeScript code needs to reference a new `vari`, function, schema, or table
via `poly.*`, **deploy those artifact files first and regenerate the SDK before
writing the TypeScript that uses the typed reference**. Use `--paths` to scope
the push to only the new files:

```bash
pnpm workflows push --paths src/<integrationName>/artifacts/vari/
pnpm workflows exec poly generate
```

Only after this step does `poly.*` expose the new path with correct types. See
`polyapi-typescript/skills/polyapi-sdk/SKILL.md` for the full deploy-first cycle rules.

## Step 6 - Write Tests

Write one `*.test.ts` file co-located with each server function
(e.g. `server/myFunction.test.ts`). Tests are mandatory — do not skip this step.

### Loading the function under test

Use the repository `require` pattern. AVA runs under ts-node so this resolves
to Node's module system:

```typescript
import test from "ava";
import poly, { polyCustom } from "polyapi";

declare const require: (modulePath: string) => any;
const mod = require("./myFunction.ts");
const myFunction: typeof import("./myFunction").default = mod.default ?? mod;
```

### Mocking `poly.*` and `polyCustom`

The `polyapi` package is a module singleton — both the test and the function
under test import the same object. Patch methods directly on `poly` before
calling the function and restore them in `t.teardown()`.

Use `test.serial` for every test that patches `poly.*` or `polyCustom` to
prevent parallel tests from clobbering each other's patches.

```typescript
function stubPoly(
    t: import("ava").ExecutionContext,
    obj: Record<string, any>,
    key: string,
    impl: (...args: any[]) => unknown,
): void {
    const original = obj[key];
    obj[key] = impl;
    t.teardown(() => {
        obj[key] = original;
    });
}

const happyRequest = {
    /* minimal valid request shape */
};

test.serial("happy path returns expected response", async (t) => {
    stubPoly(t, poly.covetrus.myContext as any, "myClientFn", async () => ({ result: "ok" }));
    stubPoly(t, poly.covetrus.utilities as any, "log", async () => undefined);
    t.teardown(() => {
        polyCustom.responseStatusCode = undefined;
    });

    const result = await myFunction(happyRequest);

    t.is(result.responseCode, "200");
});

test.serial("returns 412 when client function throws", async (t) => {
    stubPoly(t, poly.covetrus.myContext as any, "myClientFn", async () => {
        throw new Error("downstream failure");
    });
    stubPoly(t, poly.covetrus.utilities as any, "log", async () => undefined);
    t.teardown(() => {
        polyCustom.responseStatusCode = undefined;
    });

    const result = await myFunction(happyRequest);

    t.is(polyCustom.responseStatusCode, 412);
    t.true(result.orderMessage.includes("downstream failure"));
});
```

### Required coverage

Write at least one test per case:

1. **Happy path** — all `poly.*` calls succeed; assert the final response shape and
   `responseCode`
2. **Validation rejection** — the first guard throws or returns a rejection value;
   assert `412` status and the correct error message (only when Boomi evidence
   defines this gate)
3. **Branch coverage** — one test per conditional gate (e.g. `companyNumber` guard,
   delivery-option branch) derived from Boomi evidence
4. **Dependency failure** — at least one downstream `poly.*` call throws; assert
   error response shape and `polyCustom.responseStatusCode`
5. **Edge-case inputs** — any boundary inputs flagged in Boomi analysis (empty
   lists, missing optional fields, special sentinel values)

## Step 7 - Generate or Refresh Overview

Load skill:

-   `polyapi-common/skills/generate-overview/SKILL.md`

Create or refresh `workflows/src/<integrationName>/OVERVIEW.md` after
behavior-changing edits.

## Step 8 - Deployment Approval Gate

Every `pnpm workflows push` command is a deployment to the live PolyAPI
platform. Each push in Step 9 requires explicit human approval before it runs.

Before running any deployment command, show this gate:

1. `Deployment is paused at the mandatory approval gate.`
2. `Reply with explicit approval to proceed.`
3. `Approve yes/no:`

Branching rules:

-   If user answers `yes`, run the next push command, then show the gate again
    before the following one.
-   If user answers `no`, do not deploy. Ask exactly: `What should be changed before deployment?`
-   Apply user-approved changes, then show the gate again.

## Step 9 - Sync and Verify

Deployment must follow this exact phase order because server functions call
client functions via `poly.*`, and a `poly.*` path only becomes available in
the generated SDK after the target function is deployed and the SDK is
regenerated. Deploying a server function before its client function dependency
is deployed will fail at runtime.

**Phase 1 — schemas and vari** (no dependencies on other functions)

Show gate. On approval:

```bash
pnpm workflows push --paths src/<integrationName>/artifacts/schemas/
pnpm workflows push --paths src/<integrationName>/artifacts/vari/
```

**Phase 2 — client functions**

Show gate. On approval:

```bash
pnpm workflows push --paths src/<integrationName>/client/
```

**Phase 3 — regenerate SDK**

Show gate. On approval:

```bash
pnpm workflows exec poly generate
```

The new `poly.<namespace>.<integrationName>.<clientFunctionName>` paths are now
typed and available. Replace any `(poly as any)` casts in server functions with
the correctly typed `poly.*` calls before proceeding.

**Phase 4 — server functions, webhooks, and triggers**

Show gate. On approval:

```bash
pnpm workflows push --paths src/<integrationName>/server/
pnpm workflows push --paths src/<integrationName>/artifacts/webhooks/
pnpm workflows push --paths src/<integrationName>/artifacts/triggers/
```

**Phase 5 — verify**

Run unit tests (no external dependencies):

```bash
pnpm workflows test
```

Run integration (e2e) tests (requires VPN + deployed functions + live AS400):

```bash
pnpm workflows test:e2e
```

All unit tests must pass before migration completion. Run e2e tests to confirm
the full stack behaves correctly against the live environment.

## Acceptance Checklist

-   Boomi branch parity is preserved
-   Boomi map and script behavior is reproduced
-   API boundary body shapes match Boomi runtime behavior
-   Status codes match Boomi behavior
-   Approved design is analyzed with `design-analysis` before planning
-   PolyAPI constructs are mapped from Boomi evidence and documented in playback
-   Runtime variables are derived from source evidence and implementation usage
-   No secret values are stored in source files or artifacts
-   All artifact contexts start with `POLYAPI_NAMESPACE`
-   Package/dependency changes are approved before dependency files are edited
-   Overview is updated for behavior changes
-   IBM i RPG programs detected from Boomi source; registration DDL included in playback and OVERVIEW.md
-   Client functions deployed and SDK regenerated before server functions that call them
-   No `(poly as any)` casts remain after SDK regeneration
-   Sync and tests pass
