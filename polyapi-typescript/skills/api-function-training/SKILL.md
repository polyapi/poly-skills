---
name: api-function-training
description: Use when training PolyAPI API Functions from OpenAPI or Swagger in a TypeScript project, selecting operationIds, reviewing saved Poly models, or diagnosing missing trained API SDK paths.
---

# API Function Training for TypeScript

Train upstream API contracts through the project's Flow CLI, then verify the
generated TypeScript SDK. Training registers functions and schemas; invoking
an upstream API is a separate action.

## Discover the Project Command

Read the target project's instructions, package scripts, and
`pnpm flow train-openapi --help`. The commands below describe the current
TypeScript Flow template; verify support before using them in another repo.
If a flag is unavailable, inspect the installed tooling instead of inventing
syntax or silently training more operations. Keep the existing SDK version.

Use the selected `ENVPATH`, configured namespace, and saved workflow Poly setup.
Let the CLI load credentials; keep keys out of commands and reports. Existing
user authorization applies when it covers the target and resource scope;
otherwise obtain that scope before training. A request for advice authorizes
no training, upstream calls, or cleanup.

## Select, Review, Train

Run from the workspace root; replace `demo.crm` with an owned project context.
This example selects two original operation IDs:

```bash
pnpm flow train-openapi designs/crm.json --context demo.crm --operation-id validatePhone --operation-id getProfile --dry-run
pnpm flow train-openapi designs/crm.json --context demo.crm --operation-id validatePhone --operation-id getProfile --generate-only
pnpm flow train-model designs/crm.poly.json
```

The dry run is offline. `--generate-only` calls platform translation and,
by default, AI enrichment, then writes a reviewable model without upserting
resources. Review the selected functions, contexts, schemas and transport
contracts before training that model. Training can create or update resources.

| Control | Behavior |
| --- | --- |
| Repeat `--operation-id ID` | Match each original ID exactly once per input spec, before AI renaming; retain required schemas |
| Omit operation selection | Train all operations |
| `--disable-ai` | Keep translated names and metadata without AI enrichment |
| `--rename FROM TO` | Repeat for explicit model renames; review affected references and request strings |
| `--overwrite-model` | Explicitly replace an existing generated model |
| `--skip-generate` | Defer the otherwise automatic SDK regeneration |

JSON/YAML OpenAPI 3 and Swagger 2 are accepted. Folder discovery is recursive
by default; `{file}` in a context creates per-file contexts. Selection requires
bundled local references. Valid recursive schemas are supported by default.
Flow normalizes invalid schema names such as `200` and updates references in a
temporary document. Descriptions become plain text with AI enabled or disabled;
with AI enabled, cleanup also runs after enrichment. Source specs, payloads,
examples and defaults retain their contracts.

## Verify and Recover

New models use `*.poly.json`; `train-model` also accepts legacy
`*.poly-model.json`. Review or retrain existing models with `train-model`;
overwrite only when replacement is intended. Failed training may leave partial
remote state. Stop on failure, inspect the saved model and bounded diagnostics,
then retry only within the authorized scope. Training does not authorize
deletion.

After generation, verify actual `poly.*` exports and required `schemas.*` types
with the repo's type-check path. Original operation IDs may differ from final
AI-enriched names. Report registration, SDK availability and upstream execution
separately. Never invoke a mutating API merely to verify registration, or add
local typing shims to conceal missing SDK paths.

Prefer Flow's automatic regeneration: it forwards the resolved connection.
`pnpm workflows exec poly generate` uses the saved workflow SDK setup; confirm
it matches the training target when Flow environment overrides are in use.
