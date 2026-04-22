---
name: generate-schemas
description: Converts Mule RAML data types into JSON Schema files for webhook contracts. Use when a Mule project has data_types RAML files and you need schema artefacts or want to inspect the effective request and response contract.
compatibility: Requires Python 3.12+, `PyYAML`, and local access to Mule RAML data_types files.
---

# Skill: Generate Schemas

## Purpose

Use `scripts/create_schemas.py` to convert RAML type definitions into JSON Schema files that can be used directly as `eventPayloadTypeSchema` and `responsePayload` content in PolyAPI webhook artefacts.

## When to use

Use this skill when:
- A Mule project has `data_types/` RAML files that define request or response types
- You need JSON Schema representations of those types for webhook contract definitions
- You want to inspect the effective schema shape without parsing RAML manually

---

## What the script produces

| Output | Description |
|---|---|
| `schemas/<path>.json` | One JSON Schema file per input RAML file, mirroring the source directory tree |

The script writes one JSON Schema file per `.raml` file under the supplied `--data-types-dir`. It skips RAML library files whose first line is `#%RAML 1.0 Library`.

---

## Available Scripts

- `scripts/create_schemas.py` - Generates JSON Schema files from RAML `data_types/`
- `scripts/create_classes_from_raml.py` - Generates Python `TypedDict` files from RAML `data_types/`

## How to use

### Step 1 — identify the RAML data types directory

Point the script at the extracted project's `data_types/` directory, for example:

- `<PROJECT_ROOT>/META-INF/mule-src/<MULE_PROJ>/src/main/resources/api/data_types`
- `<PROJECT_ROOT>/api/data_types`

### Step 2 — run the script

Pass the input RAML directory and output schemas directory explicitly.

```bash
python scripts/create_schemas.py \
  --data-types-dir "<PROJECT_ROOT>/META-INF/mule-src/<MULE_PROJ>/src/main/resources/api/data_types" \
  --schemas-dir "<PROJECT_ROOT>/schemas"
```

Run the command from this skill directory root. Use the relative `scripts/...` path directly rather than prefixing it with `.agents/skills/...`.

| Flag | Description | Default |
|---|---|---|
| `--data-types-dir` | Directory containing RAML data type fragments | `data_types/` under repo root |
| `--schemas-dir` | Output directory for generated schemas | `schemas/` under repo root |

### Step 3 — read the output

Generated schemas are written to the requested schema directory, mirroring the input tree:

```
schemas/
  member/
    MemberProfile.json
    MemberBalance.json
```

### Step 4 — use the schemas in webhook artefacts

Copy the relevant JSON content into the webhook artefact fields:

```json
{
  "eventPayloadTypeSchema": { ...paste request type schema here... },
  "responsePayload": { ...paste response type schema here... }
}
```

---

## RAML conversion rules applied by the script

| RAML pattern | JSON Schema output |
|---|---|
| Property without `?` | Added to `required[]` array |
| Property with `?` suffix | Optional — key stripped of `?`, not in `required` |
| `date-only` type | `{"type": "string", "format": "date"}` |
| `<type> \| nil` | `{"type": "<type>", "nullable": true}` |
| `!include <path>` | Resolved recursively and inlined |
| `#%RAML 1.0 Library` first line | Skipped |

---

## Rules

- The script resolves `!include` directives relative to the file being parsed. Ensure all included fragments are present on disk.
- If a RAML file fails to parse, the script emits `{"schema": {"type": "object"}}` as a fallback and prints an error. Do not use that output as a contract; fix the source RAML or note the gap.
- Schema files in the target schemas directory are regenerated on every run. Do not edit them manually; edit the source RAML and re-run.
- RAML library files are skipped because they are not standalone types. Their types will be resolved when included by non-library RAML files.
