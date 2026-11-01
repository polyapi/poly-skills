---
name: api-function-training
description: Use when training PolyAPI API Functions from OpenAPI or Swagger in a Python project, selecting operationIds, reviewing saved Poly models, or diagnosing missing trained API SDK paths.
---

# API Function Training for Python

Train upstream API contracts through the project's Flow tooling, then verify
the native Python SDK. Registering an API Function does not invoke the upstream
service.

## Discover the Project Command

Read the target project's instructions and
`uv run --locked python -m cli.operations train-openapi --help`. These examples
describe the current Python Flow template. Verify support in the active repo;
do not install Flow, change SDK versions, or guess unsupported flags merely
because a copied skill mentions them. After loading the project's shell helper,
`flow train-openapi` and `flow train-model` are equivalent entry points.

Use the selected `ENVPATH`, owned namespace and configured native SDK connection.
Let the CLI load credentials and verify the environment pin. Preserve branch,
production and OTP safeguards; a required `TARGET_ENV_ID` pin belongs in the
selected env file, not just an exported variable. Keep keys out of commands
and reports.
Existing authorization applies when it covers the target and resource scope;
obtain missing scope before training. Advice alone authorizes no platform calls.

## Select, Review, Train

Run from the project root; use an owned context in place of `demo.crm`:

```bash
uv run --locked python -m cli.operations train-openapi designs/crm.json --context demo.crm --operation-id validatePhone --operation-id getProfile --dry-run
uv run --locked python -m cli.operations train-openapi designs/crm.json --context demo.crm --operation-id validatePhone --operation-id getProfile --generate-only
uv run --locked python -m cli.operations train-model designs/crm.poly.json
```

The dry run is offline. `--generate-only` calls platform translation and,
by default, AI enrichment, then writes a model without upserting resources.
Review selected functions, final names, contexts, schemas and transport contracts
before training the saved model. Training can create or update resources.

| Control | Behavior |
| --- | --- |
| Repeat `--operation-id ID` | Match each original ID exactly once per input spec, before AI renaming; retain required schemas |
| Omit operation selection | Train all operations |
| `--disable-ai` | Keep translated names and metadata without AI enrichment |
| `--rename FROM TO` | Repeat for explicit model renames; review affected references and request strings |
| `--overwrite-model` | Explicitly replace an existing generated model |
| `--skip-generate` | Defer the otherwise automatic native SDK regeneration |

OpenAPI 3 and Swagger 2 JSON/YAML are accepted; Swagger conversion is automatic.
Folder discovery is recursive by default; `{file}` creates per-file contexts.
Selection requires bundled local references. Valid recursive schemas are
supported by default. Invalid schema names such as `200` are normalized with
references updated, while the original spec remains unchanged. Descriptions
become plain text with AI enabled or disabled, including after enrichment.
Payloads, examples and defaults retain their contracts.

## Verify and Recover

Models use `*.poly.json`. Review or retry an existing model with `train-model`;
overwrite only when replacement is intended. Failed training may leave partial
remote state: stop, inspect the saved model and bounded diagnostics, then retry
only within the authorized scope. Training does not authorize deletion.

Verify final generated API names, their `_async` variants where provided, and
the repo's native SDK type/import checks. AI-enriched names may differ from the
original IDs. Report registration, SDK availability and upstream execution
separately; never invoke a mutating API merely to prove registration.

Some pinned Python SDK versions skip recursive schema types during generation.
Successful platform training does not prove that those types were generated;
surface warnings and missing exports without replacing contracts with generic
types or silently upgrading the SDK. Prefer Flow's automatic regeneration so
it uses the resolved target. If deferred, use the repo's documented native
`python -m polyapi generate` path with that same connection.
