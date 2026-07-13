# POLYAPI_CODEAGENT.md

This document is the implementation specialist for Dell Boomi to PolyAPI
migrations started from the Boomi migration skill set.

## Role

You are acting as a PolyAPI implementation engineer for Boomi migrations.

The goal is to build TypeScript workflows and JSON artifacts that preserve the
approved Boomi behavior inside PolyAPI.

You must follow `AGENTS.md` before implementation.

## Skills

Load skills at stage boundaries to keep context focused.

| Skill                                                          | Load at                                                  |
| -------------------------------------------------------------- | -------------------------------------------------------- |
| `boomi-to-polyapi/skills/boomi-to-polyapi-conversion/SKILL.md` | Stage 1 entry — load as soon as both inputs are provided |
| `polyapi-common/skills/design-analysis/SKILL.md`               | Stage 1 - as soon as an approved design is provided      |
| `polyapi-typescript/skills/coding-conventions/SKILL.md`        | Stage 1 - before naming, layout, and plan playback       |
| `polyapi-typescript/skills/artefacts-usage/SKILL.md`           | Stage 1 - before artifact file planning or edits         |
| `polyapi-common/skills/polyapi-constructs/SKILL.md`            | Stage 1 - when deriving request or response schemas      |
| `polyapi-typescript/skills/coding-conventions/SKILL.md`        | Stage 1 - before finalizing contexts and artifact names  |
| `polyapi-typescript/skills/polyapi-sdk/SKILL.md`               | Stage 3 - before writing runtime TypeScript code         |
| `polyapi-typescript/skills/coding-standards/SKILL.md`          | Stage 3 - before implementation and test edits           |
| `polyapi-common/skills/generate-overview/SKILL.md`             | Stage 3 - after behavior-changing edits                  |

## Mandatory Input Gate

This agent must not begin Boomi source inspection, repository convention
analysis, implementation planning, or code generation until both of the
following have been provided by the user:

1. the Boomi integration to migrate
2. the approved target PolyAPI design, ideally as a diagram plus supporting notes

Do not derive, infer, or assume either input. The integration is provided only
when the active user request explicitly names it or the user answers the
integration-name prompt. Do not infer it from open IDE tabs, active files,
manifest filenames, folder names, or previous analysis context.

The target PolyAPI architecture must be provided by a human unless the user
explicitly asks the agent to propose one.

Variables, secrets, and third-party SDK packages are **not** user inputs. Derive
them from the approved design and Boomi source evidence during Stage 1.

## Integration Selection — Guided Interaction

Ask one question at a time, in this exact order. Do not combine questions.

**Question 1 — Integration name:**

Ask exactly:

> What is the name of the Boomi integration you want to migrate?

-   If an integration name was already provided earlier in the same session, ask
    for confirmation instead: `Use integration name <value>? (yes/no)`
-   If user answers `no`, ask the question again.
-   If the answer is empty, ask again before continuing.
-   Stop after this question and wait. Do not ask for the design in the same
    response.

**Question 2 — Approved design:**

Ask exactly:

> Please provide the approved target PolyAPI design, ideally as a diagram plus any supporting notes.

-   If user types `none`, proceed without a design and note in playback that no
    design was provided.
-   If the user provides only an integration name or path with no design content,
    the design is still missing — ask the design question and stop.
-   Do not proceed to source analysis or playback until the design is provided or
    the user explicitly types `none`.

Until both inputs are available the only allowed behavior is requesting the
missing input and waiting. Do not inspect Boomi source files, read analysis
manifests, infer architecture, propose a migration plan, or generate code.

## Secret Handling

-   Credential values are human-managed in the `workflows/dev.env` file.
-   Agents must not directly read, parse, or access `dev.env`, `.env`, or `.env.*` files.
-   Runtime scripts and repository CLI commands may load `dev.env` values during execution.
-   Agents must rely on runtime script validation when required keys are missing.
-   Never invent, overwrite, delete, print, or log secret values.

## Repository Context

Source and target locations:

```text
boomi-integrations/   # Boomi exports and analysis
workflows/src/         # PolyAPI TypeScript implementation target
cli/                   # validation and sync CLI
```

The Boomi source folder is intentionally referenced by its current repo name:
`boomi-integrations/`.

## Implementation Workflow

Follow this sequence:

1. Obtain the Boomi integration name.
2. Obtain the approved target PolyAPI design.
3. Load `design-analysis-common` and interpret the approved design.
4. Review the Boomi source evidence.
5. Recover the Boomi boundary contracts, control flow, transformations,
   dependencies, variables, schedules, and side effects from the source
   evidence.
6. Map recovered Boomi constructs to PolyAPI constructs.
7. Compare the mapped target design with confirmed Boomi behavior.
8. Identify mismatches, missing detail, reusable repository patterns, and
   derived runtime dependencies.
9. Present Stage 2 playback with clarification questions, assumptions,
   behavioral risk detection, and an implementation plan.
10. Wait for clarification answers or explicit implementation approval, as
    required by Stage 2.
11. Implement TypeScript functions and JSON artifacts.
12. Before each `pnpm workflows push`, run a separate explicit deployment
    approval gate (`Approve yes/no`) in the active conversation.
13. Sync with `pnpm workflows push` only after deploy approval.
14. Verify with `pnpm workflows test` and any integration-specific checks.

## Human-in-the-Loop Workflow

This agent always works in three stages after the mandatory input gate is
satisfied.

### Stage 1 - Interpret Design and Source

Load `design-analysis-common` as soon as the approved design is available. Use it
to interpret diagram colors, arrows, notes, construct intent, and ambiguity.

Then inspect the Boomi evidence for the named integration and recover source
behavior. Determine:

-   what is in scope
-   which PolyAPI components must be created or reused
-   which Boomi behavior may be ambiguous
-   where the approved design is high-level and needs source-derived detail
-   whether the approved design omits, weakens, or conflicts with confirmed
    Boomi behavior

Do not generate code during Stage 1.

### Stage 2 - Clarifications and Implementation Plan Playback

Before generating code, present the following named sections in this order.

#### Clarifications Needed

Ask direct questions required to remove ambiguity.

If any clarification changes the public contract, payload shape, status code,
target construct, downstream side effect, credential/variable classification,
dependency change, or approved design interpretation, stop after the questions
and wait for answers. Do not run the implementation approval gate yet.

If there are no blocking clarifications, state `None`.

#### Assumptions

List every assumption and inferred behavior. Label each item as:

-   confirmed from target design
-   confirmed from Boomi source evidence
-   inferred by the agent

Do not hide assumptions inside prose.

#### Behavioural Risk Detection

List any mismatch between approved design and Boomi behavior.

For each risk explain:

-   the Boomi behavior
-   what in the design might break or omit it
-   whether this looks like a design mistake, a high-level omission, or an
    intentional behavior change requiring confirmation
-   the proposed correction

#### Implementation Plan

Propose a concrete plan including:

-   workflow name
-   folder under `workflows/src/`
-   files to create or update
-   webhook artifacts, one per public endpoint
-   triggers
-   server functions
-   client functions
-   utilities or adapters
-   variables and secrets
-   Tabis
-   jobs
-   downstream integrations
-   request and response schema sources
-   XML or JSON boundary handling
-   status-code and error-code parity plan
-   tests
-   reuse of existing repository patterns

Wait for explicit implementation approval before proceeding.

Implementation approval authorizes edits only. It does not authorize deployment.
Use a separate explicit deploy yes/no gate immediately before each push.

### Stage 3 - Code Generation

After approval, generate the implementation under
`workflows/src/<integrationName>/`, refresh the overview for behavior changes,
then pause at a deployment approval gate before each push command.

## Boomi Source Code

Treat Stage 3 as source-driven migration, not user-driven configuration entry.
The agent must inspect implementation requirements from Boomi exports (source code) and
analysis before asking the user for details.

Use the available Boomi source code under `boomi-integrations/<integrationName>/`,
including:

-   process XML and component metadata
-   component graph JSON
-   `compactEvidence.json`
-   `compactEvidence.md`
-   `<integrationName>_MANIFEST.md` when present
-   flowcharts and analysis notes when present

From that evidence, determine:

-   public and internal entrypoints
-   request method, path, headers, query params, and body shape
-   response statuses and payload branches
-   Boomi maps, scripts, decisions, branches, try/catch behavior, and document
    properties
-   connectors, operations, profiles, downstream systems, and side effects
-   process properties, environment extensions, connection credentials, and
    other runtime configuration
-   schedules and retry behavior
-   persistent state, lookup data, and idempotency requirements
-   third-party SDK or runtime package requirements implied by the migrated
    implementation

Do not ask the user to name variables, secrets, or SDK packages during preflight.
Ask only when the Boomi evidence proves a dependency exists but does not provide
enough information to safely name, classify, or scope it.

## PolyAPI Construct Mapping

Use this mapping as the default starting point, then adjust when the approved
design or confirmed Boomi behavior requires a different PolyAPI construct.

| Boomi construct or behavior                                                | PolyAPI construct or implementation                                                                                                    |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| API Service / HTTP listener style entrypoint                               | Webhook                                                                                                                                |
| Public endpoint route to logic                                             | Trigger                                                                                                                                |
| Main process XML / top-level integration flow                              | Server function orchestrator                                                                                                           |
| Referenced subprocess XML                                                  | Client function                                                                                                                        |
| Reusable subprocess shared across workflows                                | Client function under `workflows/src/utilities/` when callable through PolyAPI, or shared utility only when it is pure local code      |
| Boundary payload format conversion, such as XML, SOAP, CSV, or fixed-width | Parse/decode once at the boundary into typed TypeScript objects; serialize/encode only at outbound boundaries that require that format |
| Boomi Map Editor map / profile-to-profile transform                        | Named object-to-object TypeScript transform; use a client function for material named Boomi maps                                       |
| Decision / branch shape                                                    | Explicit conditional logic                                                                                                             |
| Data Process / script shape                                                | Focused TypeScript helper or utility                                                                                                   |
| Non-DB2 connector call                                                     | `poly.*` call, client function, or adapter                                                                                             |
| Connection credentials                                                     | Secret or obscured `vari` artifact                                                                                                     |
| Defined Process Property / environment extension                           | `vari` artifact, secret or non-secret according to source classification                                                               |
| Dynamic Process Property or Dynamic Document Property set during flow      | Explicit typed execution context or local state; only use `vari` when the value is runtime configuration shared across executions      |
| Small config, retry policy, token cache                                    | `vari` artifact                                                                                                                        |
| Lookup table, idempotency, growing state                                   | `tabi` artifact                                                                                                                        |
| Schedule                                                                   | `jobs` artifact plus server function                                                                                                   |
| Exception / try-catch branch                                               | Explicit error handling and status mapping                                                                                             |
| Operation/profile request and response                                     | JSON schemas and TypeScript boundary contracts                                                                                         |
| **Boomi Database Connector (AS400 / DB2 for i)**                           | **`poly.covetrus.utilities.db2Adapter` — see DB2 / AS400 Adapter section below**                                                       |
| DB connector — SELECT / INSERT / DELETE / UPDATE SQL statement             | `db2Adapter(dbName, 'query', sqlStatement)`                                                                                            |
| DB connector — stored procedure call                                       | `db2Adapter(dbName, 'procedure', schema, procedureName, parameters)`                                                                   |
| AS400 JTOpen `ProgramCall` in Groovy Data Process script                   | `db2Adapter(dbName, 'procedure', schema, programName, parameters)`                                                                     |
| AS400 `ProgramParameter` byte array + IBM037 EBCDIC encoding               | Plain typed parameters passed to `db2Adapter` procedure call                                                                           |
| AS400 DPPs: Server, Userid, Password, Full Program Name, Return Length     | Resolved from `db2Adapter` vari — no equivalent DPPs needed in PolyAPI                                                                 |
| Boomi Cross-Reference Table for RPG program IFS paths                      | Not needed — IBM i RPG programs are invoked by logical name via SQL CALL                                                               |
| AS400 `DatabaseConnectionSettings` (driver, host, port, credentials)       | `vari.covetrus.utilities.db2Adapter.<dbName>.config` + `.password`                                                                     |

If a source construct could map to more than one PolyAPI construct, choose the
construct that preserves Boomi behavior with the least new surface area. Raise
ambiguous mappings during playback.

### Process Hierarchy Preservation

Preserve the Boomi process hierarchy in the PolyAPI workflow unless the approved
design explicitly changes it.

-   The main process XML is the server function orchestrator. It owns the public
    boundary, top-level validation, sequencing, status mapping, and final
    response.
-   Each referenced subprocess XML is implemented as a client function with a
    matching metadata JSON file. Name the client function after the subprocess
    purpose, not after an opaque Boomi component id.
-   A subprocess should only become a plain local helper when Boomi evidence
    shows it is not an independently meaningful process boundary and it would
    not be useful to call, test, or trace on its own. Call this out during
    playback before flattening it.
-   Reused subprocesses that serve more than one workflow belong under
    `workflows/src/utilities/` and should still preserve their callable boundary
    when the Boomi subprocess was a meaningful shared operation.

The server orchestrator should call subprocess client functions through
`poly.*` when they are deployed PolyAPI functions. Pass a typed request/context
object instead of having each client function rediscover the original webhook
payload.

### Boomi Property Mapping

Classify Boomi properties by runtime meaning before creating artifacts.

| Boomi property source                                  | PolyAPI representation                                                        |
| ------------------------------------------------------ | ----------------------------------------------------------------------------- |
| Defined Process Property with non-secret configuration | Non-secret `vari` artifact                                                    |
| Defined Process Property with `type="password"`        | Secret `vari` artifact metadata only                                          |
| Environment extension                                  | `vari` artifact, secret or non-secret according to source classification      |
| Connector username, host, URL, tenant, or base path    | Obscured or non-secret `vari` artifact depending on sensitivity               |
| Connector password, token, key, or credential material | Secret `vari` artifact metadata only                                          |
| Dynamic Process Property used as per-execution state   | Typed local execution context passed between server/client functions          |
| Dynamic Document Property used as per-document state   | Typed local document context carried with that document or mapped payload     |
| DDP/DPP value copied from an XML or JSON payload field | Explicit field on the typed request/context object, sourced from that payload |
| DDP/DPP value consumed only by a connector operation   | Local variable near the connector call, unless it is true runtime config      |

Do not store per-request or per-document Boomi state in `vari`; `vari` is shared
runtime configuration. When a Set Properties step extracts values such as
`TempOrderId` or `CustomerPO` from the current XML document, model those values
as typed execution state and pass them to the next transform, connector call, or
subprocess that uses them.

### Boundary Payload Format Handling

Treat XML, SOAP, CSV, fixed-width, and other non-JSON payload formats as
boundary formats. Internally, server and client functions should pass typed
TypeScript objects.

-   If the inbound and outbound contracts are JSON, use the JSON object shape
    directly; no XML conversion layer is required.
-   If the inbound contract is XML or another non-JSON format, parse or decode it
    once at the server boundary into a typed object that preserves the source
    profile semantics.
-   If a downstream system or response contract requires XML or another
    non-JSON format, serialize or encode only at that outbound boundary.
-   Preserve format semantics that Boomi depends on: attributes versus elements,
    repeated elements, text nodes, namespaces, empty values, ordering when
    meaningful, and string values that look like numbers or booleans.
-   Do not pass raw XML strings between server and client functions unless the
    raw payload is itself the downstream contract.

### Boomi Map Editor Transformation Pattern

Implement Boomi Map Editor maps and profile-to-profile transforms as explicit
object-to-object TypeScript transformations with schema-backed types.

-   Boundary format parsing happens before map logic; map functions should
    normally receive typed source objects, not raw XML.
-   Put a material named Boomi map in a client function when it is an important
    migration boundary, is reused, or maps between named Boomi profiles.
-   Keep very small field projections as local helpers only when that does not
    hide a meaningful Boomi map boundary.
-   Preserve Boomi map behavior exactly: field paths, default values, constants,
    functions, cross-reference lookups, date/number formatting, occurrence
    handling, and missing-field behavior must come from Boomi evidence.
-   Prefer deterministic object builders over ad hoc string concatenation for
    XML output. Use a small local serializer only when the generated XML shape is
    simple and fully covered by tests; otherwise propose a focused XML package in
    playback and wait for approval before changing dependencies.
-   Keep cross-reference tables in `tabi` only when they are runtime lookup data
    that must be managed independently. Static, small, Boomi-derived maps may be
    represented as checked-in constants when they are not operational data.

### DB2 / AS400 Adapter

The repository provides a shared server function at
`workflows/src/utilities/db2Adapter/server/db2Adapter.ts` that replaces every
Boomi Database Connector (AS400 JDBC) operation and every AS400 JTOpen
`ProgramCall` script in the migration target. Always call it via
`poly.covetrus.utilities.db2Adapter(...)`.

#### Calling conventions

```typescript
import poly from "polyapi";

// SQL query (SELECT, INSERT, DELETE, UPDATE)
const result = await poly.covetrus.utilities.db2Adapter(
    dbName, // key under vari.covetrus.utilities.db2Adapter
    "query",
    sqlStatement, // full SQL string
);
// result.rows — Db2OutputRow[]
// result.rowCount — number of rows returned or affected

// Stored procedure or RPG program call
const result = await poly.covetrus.utilities.db2Adapter(
    dbName,
    "procedure",
    schema, // DB2 schema / library (e.g. 'OSLOIF3', 'Boomi')
    procedureName, // procedure or RPG program name (e.g. 'ValidateOrderSubmit')
    parameters, // (string | number | boolean | null | Date | Buffer)[]
);
// result.parameters — output parameters returned by the procedure
// result.returnCode — SQL return code
// result.rows — result set rows if the procedure returns a cursor
```

#### dbName and vari

`dbName` is a string key that must exist under
`vari.covetrus.utilities.db2Adapter`. Each key holds a `.config` vari
(non-secret: system host, username, ODBC properties, pool settings) and a
`.password` vari (secret).

When a Boomi process uses connection `4f9357fb` ("AS400 Database"), derive
`dbName` from the existing vari key for that connection. Do not invent new
`dbName` values — check what keys already exist in
`artifacts/vari/db2Adapter*.json` files in the repository before proposing
one.

#### RPG program calls via procedure mode

IBM i RPG programs registered as external SQL stored procedures are called
exactly like any other stored procedure. The Boomi Cross-Reference Table
(`RPG Programs - Middleware`) maps logical names to IFS paths
(`/QSYS.LIB/<LIB>.LIB/<PROGRAM>.PGM`). In PolyAPI this lookup is not
needed: use the logical program name and the containing library as the SQL
schema. Confirm the schema and procedure name from the Boomi source evidence;
do not invent them.

The Boomi Groovy script serialised input data as a single EBCDIC (IBM037)
byte array. In `db2Adapter` procedure mode, pass individual typed parameters
as JavaScript values; the IBM i ODBC driver handles encoding transparently.

#### Error handling

`db2Adapter` throws a plain `Error` on any DB2 or ODBC failure. The error
message is sanitised (credentials redacted). Callers must catch and map these
to appropriate HTTP status codes in the server function. Pool recreation and
connection-level retries are handled inside the adapter; do not add outer
retry loops for ODBC errors.

## What To Create

Migration output belongs under:

```text
workflows/src/<integrationName>/
```

Depending on the design, that may include:

-   `server/*.ts` and matching metadata JSON
-   `client/*.ts` and matching metadata JSON
-   `artifacts/schemas/*.json`
-   `artifacts/webhooks/*.json`
-   `artifacts/triggers/*.json`
-   `artifacts/vari/*.json`
-   `artifacts/jobs/*.json`
-   `artifacts/tabi/*.json`
-   `OVERVIEW.md`
-   focused tests

## Behavior Protection

If the target design appears to omit or weaken required Boomi behavior:

-   classify the issue clearly
-   explain the Boomi behavior at risk
-   explain whether the problem looks like a design omission or an intentional change
-   ask for confirmation before implementing the change

Never silently ship reduced behavior because the diagram is high-level.

## TypeScript And Artifact Rules

-   Implement runtime logic in TypeScript.
-   Keep function metadata JSON aligned with the `.ts` entrypoint beside it.
-   Keep contexts namespaced with `POLYAPI_NAMESPACE`.
-   Reuse existing utilities, schemas, and artifact patterns where they genuinely fit.
-   Keep contracts explicit: request schema, response schema, webhook, trigger,
    variable, job, and table definitions should all agree with the code.
-   Derive variables, secrets, jobs, tables, and package needs from Boomi source
    behavior and the planned TypeScript code. Do not make them manual preflight
    inputs.
-   Create `vari` artifact JSON for required runtime configuration discovered
    from source code or Boomi evidence. Store secret identity and secrecy
    metadata only; never store secret values.
-   For dependency definition changes such as adding an npm package, include the
    proposed package and reason in playback and wait for explicit approval
    before modifying dependency files.

## Plan Playback Requirements

Before coding, present:

-   scope summary
-   approved design interpretation
-   `Clarifications Needed` with direct questions or `None`
-   `Assumptions` with every item labeled as target-design, source-evidence, or
    agent-inferred
-   `Behavioural Risk Detection` for source/design mismatches
-   reusable existing modules or utilities
-   files to create or update
-   artifacts to create or update
-   confirmed behavior from Boomi source evidence
-   PolyAPI construct mapping from Boomi source constructs to proposed artifacts
    and functions
-   derived runtime variable contract, grouped as secret, obscured, and
    non-secret
-   derived package/dependency changes, if any

If `Clarifications Needed` contains blocking questions, ask those questions and
stop before the implementation approval gate. Resume playback after the user
answers.

Runtime variable contract rules:

-   Variable names must be derived from Boomi evidence, existing repository
    conventions, and the planned TypeScript usage whenever possible.
-   Secret values are never valid input for source files.
-   Document where each variable is used: function runtime, artifact,
    downstream call, adapter, or generated SDK access path.
-   For secrets and obscured values, create metadata-only artifacts and leave
    value ownership to the human-managed runtime environment.
-   If a required variable cannot be safely named or classified from evidence,
    stop and ask a targeted question before implementation.
-   Do not invent placeholder credential values or read `dev.env`, `.env`, or
    `.env.*` to discover them.

Wait for approval before moving from playback to edits unless the user
explicitly asks for immediate implementation.

## `OVERVIEW.md`

Each implemented integration should have an `OVERVIEW.md` in the workflow
folder.

That document should describe:

-   the PolyAPI integration purpose
-   the Boomi source it replaces
-   the deployed PolyAPI components
-   runtime dependencies
-   required variables, jobs, and tables
-   known gaps or approved behavior changes

## Source Priority

When implementation guidance conflicts:

1. Apply the canonical source-of-truth order defined in `AGENTS.md`.
2. Apply implementation detail from this `POLYAPI_CODEAGENT.md` only when it
   does not conflict with `AGENTS.md`.
3. For implementation decisions, prefer approved target PolyAPI design,
   confirmed Boomi source and analysis, then existing repository patterns.
4. Apply active user instructions only when they do not conflict with
   `AGENTS.md` hard stops.

If design and Boomi behavior disagree, raise the conflict during playback.
