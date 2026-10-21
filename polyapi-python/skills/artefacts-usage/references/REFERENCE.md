# PolyAPI Python artefacts reference

## Workflow placement

Resolve `<workflow_root>` from the active repository (`src/`, `workflows/src/`,
or another configured root). This is a menu of supported locations, not a list
of empty directories to create:

```text
<workflow_root>/<workflow>/
  OVERVIEW.md
  server/<name>_sfx.py
  client/<name>_cfx.py
  tests/test_<behavior>.py
  artefacts/
    schemas/
    webhooks/
    triggers/
    vari/
    jobs/
    tabi/
    ai-functions/
    canopy/
    subscriptions/
    specs/
```

Use the same relevant structure under `<workflow_root>/utilities/<utility>/`
for shared deployed behavior. Supported resource kinds come from the local
sync tool. Keep inactive design examples outside its discovery paths.

A `types/` folder does not make its modules deployable. If the deployer uploads
one source file, keep required runtime types/helpers in that file or reuse a
deployed function via the SDK. Follow the repository's established location
for one-off operator scripts outside deployable-function discovery.

## Contract selection

The selected instance's `/swagger-json` describes its platform API. Checked-in
schemas and Flow transformations describe local validation and translation to
that API. On mismatch, identify the selected target/version and refresh through
the supported command with approval for the effect; do not silently switch hosts
or loosen schemas. No region is the universal contract source.

Common mappings, to verify against that contract:

| Artefact category | API resource | Typical create DTO |
| --- | --- | --- |
| `webhooks/` | `/webhooks` | `CreateWebhookHandleDto` |
| `triggers/` | `/triggers` | `CreateTriggerDto` |
| `vari/` | `/variables` | `CreateVariableDto` |
| `schemas/` | `/schemas` | `CreateSchemaDto` |
| `jobs/` | `/jobs` | `CreateJobDto` |
| `tabi/` | `/tables` | `CreateTableDto` |

For `ai-functions/`, `canopy/`, and `subscriptions/`, inspect the installed
platform contract and local adapter. Do not infer endpoint names from folder
names. The API calls Tabi resources tables.

## Resource checks

### Webhooks and triggers

- Preserve the endpoint's intended method, slug, subpath, path/query mapping,
  request/response schemas, and HTTP status behavior.
- Follow the project's explicit endpoint or router design. Do not introduce
  catch-all routes as a workaround for incomplete endpoint contracts.
- Verify API-key requirements and security-function acceptance/rejection.
- Check paired trigger destinations, exact arguments, response handling, error
  routing, and enabled states together.
- Use XML parser options only for an actual XML boundary and preserve the
  upstream contract's array and normalization behavior.

### Vari

- Verify context, name, type, secrecy level, and supported value format.
- Store placeholder metadata only for secrets. Set real values through the
  authorized target mechanism; do not persist them in artefacts or logs.
- Distinguish NONE configuration, sensitive OBSCURED/PARTIAL data, and opaque
  SECRET injection. Verify read semantics in the pinned SDK and selected target;
  do not cache sensitive values.
- Do not overwrite an existing secret with an empty placeholder during sync.

### Jobs, AI tools, and references

Prefer portable references when the local adapter supports them, for example:

```json
{"functionName": "process_event", "functionContext": "example.workflow"}
```

```json
{"variableName": "service_key", "variableContext": "example.workflow"}
```

These are reference objects, not standalone create requests. Follow the
resource's actual enclosing schema. Resolve them in the selected environment;
do not retain hardcoded IDs from another instance.

For jobs, verify schedule units, timezone behavior where supported, argument
mapping, and intended enabled state. For AI functions, verify model/provider
availability, tool signatures, secret bindings, and response schema. Training
OpenAPI specs and invoking AI are separate effects from a local validation.

### Tabi, Canopy, and subscriptions

- Match Tabi column/schema and row shapes to the current API and SDK contract.
  Do not assume illustrative `columns`/`rows` fields are accepted create payloads.
- Resolve Canopy identity using the local adapter's supported ID/name/subpath
  rules. Preserve existing identity and descriptions; do not infer orphan
  ownership merely from local absence.
- Resolve GraphQL subscription destinations and provider configuration in the
  selected target. Inspect whether the update path recreates the stream. A
  delete/create can reset offsets or interrupt delivery and needs the existing
  explicit confirmation.

## Safe reconciliation

Establish ownership from the declared namespace and the adapter's resource
identity rules. Jobs/triggers may lack a context and require owned prefixes and
verified destination function IDs. External references do not broaden ownership.

Inspect a scoped dry run before sync. A rename can create a new resource and
make an old identity appear orphaned. Treat deletion and stream recreation as
separate reviewed effects, with dependency checks and independent readback.

## Workflow overview

Record purpose, entrypoints, resources, configuration names/secrecy levels,
external effects, enabled states, failure behavior, and focused verification.
Include migration provenance or parity notes only when a migration is actually
part of the project. Distinguish local checks from deployed evidence.
