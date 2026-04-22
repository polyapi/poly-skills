# compress-source Reference

## Purpose

Three scripts run in sequence to generate:

| Output | Produced by | Used for |
| --- | --- | --- |
| `schemas/` | `scripts/create_schemas.py` | JSON schema files from RAML data types |
| `compressed.txt` | `scripts/xml_to_py.py` | Readable flow tree, VARIS, schedulers, resolved flow-refs |
| `webhooks.jsonl` | `scripts/link_schema_to_wbhk.py` | One schema-enriched JSON object per public endpoint |

After these scripts run, all RAML, data-type fragments, and Mule XML have been processed.
The agent must not open any of those source files. Use only `compressed.txt` and `webhooks.jsonl`.

## Step 1 — Reuse known project root when possible

If `<PROJECT_ROOT>` was already confirmed during project selection, reuse it.

Only ask the user:

> What is the path to the extracted MuleSoft project folder?
> (e.g. `/c/client_projects/gha-mule/argos`)

Call this `<PROJECT_ROOT>`.

## Step 2 — Discover paths

From `<PROJECT_ROOT>`, discover the following without asking the user:

1. **Inner project folder** — list `<PROJECT_ROOT>/META-INF/mule-src/` to find the subfolder name.
   Call this `<MULE_PROJ>`.
2. **Mule XML files** — list `<PROJECT_ROOT>/META-INF/mule-src/<MULE_PROJ>/src/main/mule/`:
   - Main APIKit router XML
   - Global config XML, usually `_global.xml`
   - Implementation XMLs under `implementation/`
3. **RAML and data types** — list `<PROJECT_ROOT>/META-INF/mule-src/<MULE_PROJ>/src/main/resources/api/`:
   - RAML file
   - `data_types/` subdirectory
4. **Filter file** — check whether `<PROJECT_ROOT>/interested_hooks.txt` exists.

## Step 3 — Confirm only when needed

Present a path summary:

```text
PROJECT_ROOT  : <PROJECT_ROOT>
MULE_PROJ     : <MULE_PROJ>

flow_xml      : .../mule/<flow_xml>
global_xml    : .../mule/_global.xml
xml_files     : .../mule/implementation/<impl_xml>  [one line per file]

raml          : .../resources/api/<raml_file>
data_types    : .../resources/api/data_types/

schemas_dir   : <PROJECT_ROOT>/schemas/
compressed    : <PROJECT_ROOT>/compressed.txt
webhooks      : <PROJECT_ROOT>/webhooks.jsonl

filter_file   : <PROJECT_ROOT>/interested_hooks.txt  [omit line if not found]
```

If any discovered path is ambiguous, missing, or surprising, wait for confirmation or corrections before running scripts.
If the paths are clear and complete, do not spend an extra turn asking for confirmation again.

## Step 4 — Run scripts in order

Run these commands from the `compress-source` skill directory root. Use the relative `scripts/...` paths directly. Stop on any error.

### Script 1 — scripts/create_schemas.py

```bash
python scripts/create_schemas.py \
  --data-types-dir "<PROJECT_ROOT>/META-INF/mule-src/<MULE_PROJ>/src/main/resources/api/data_types" \
  --schemas-dir "<PROJECT_ROOT>/schemas"
```

### Script 2 — scripts/xml_to_py.py

```bash
python scripts/xml_to_py.py \
  --flow-xml "<PROJECT_ROOT>/META-INF/mule-src/<MULE_PROJ>/src/main/mule/<flow_xml>" \
  --global-xml "<PROJECT_ROOT>/META-INF/mule-src/<MULE_PROJ>/src/main/mule/_global.xml" \
  --xml-files "<PROJECT_ROOT>/META-INF/mule-src/<MULE_PROJ>/src/main/mule/implementation/<impl_xml>" \
  --out "<PROJECT_ROOT>/compressed.txt"
```

- If there are multiple implementation XMLs, add one `--xml-files <path>` per file.
- Add `--filter-file "<PROJECT_ROOT>/interested_hooks.txt"` only if the file exists.

### Script 3 — scripts/link_schema_to_wbhk.py

```bash
python scripts/link_schema_to_wbhk.py \
  --raml "<PROJECT_ROOT>/META-INF/mule-src/<MULE_PROJ>/src/main/resources/api/<raml_file>" \
  --schemas-dir "<PROJECT_ROOT>/schemas" \
  --webhooks "<PROJECT_ROOT>/webhooks.jsonl" \
  --out "<PROJECT_ROOT>/webhooks.jsonl"
```

## Step 5 — Verify outputs

Confirm these files exist and are non-empty before proceeding:

- `<PROJECT_ROOT>/compressed.txt`
- `<PROJECT_ROOT>/webhooks.jsonl`
- `<PROJECT_ROOT>/schemas/*.json` (at least one file)

Report the number of lines in `webhooks.jsonl`.
If any output is missing or empty, report the specific error and stop.
If schema generation reported parse failures, or if any generated schema used the fallback generic object shape, report that explicitly and stop.

## Output interpretation

### compressed.txt

Read this for everything about flow logic. Do not open raw XML for anything visible here.

| Section | What it contains |
| --- | --- |
| MULE FLOW TREE | Every flow and sub-flow with steps indented; flow-refs expanded inline |
| CONFIG-REFS → VARIS | All `${...}` property placeholders required at runtime |
| SCHEDULERS | Any scheduler/job definitions extracted as PolyAPI job seeds |
| Webhooks (at end) | Flow-name-to-route mapping used by Script 3 |

Use `compressed.txt` to determine:

- What each flow does step by step
- Whether any flow produces or consumes XML
- What error handlers exist and what HTTP status codes they return
- Which property keys and secrets are required

### webhooks.jsonl

Each line is a JSON object for one public endpoint.

Fields populated by the scripts — treat as authoritative:

- `subpath`
- `method`
- `eventPayloadTypeSchema`
- `responsePayload`

Fields that may need agent correction before writing artefact files are covered in Stage 3 of `POLYAPI_CODEAGENT.md`.
