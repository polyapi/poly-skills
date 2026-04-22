---
name: compress-source
description: Generates compressed Mule migration artefacts from Mule XML and RAML. Use when starting Stage 1 analysis, before reading raw Mule source, or when you need compressed.txt and webhooks.jsonl for a project.
compatibility: Requires Python 3.12+, `PyYAML`, `lxml`, and local access to extracted Mule project files.
---

# Skill: compress-source

Produces the compressed Mule source artefacts that all later stages consume.
Run this skill **once per project** at the start of Stage 1, before reading any XML.

If the project only exists as a jar under `jars/` and does not yet exist as an extracted top-level folder, run `extract-redact-mule-jars` first.

---

## Workflow

1. Use the confirmed `<PROJECT_ROOT>` from project selection if it is already known. Ask the user for `<PROJECT_ROOT>` only when it has not been established yet.
2. Discover the inner Mule project folder, router XML, global XML, implementation XMLs, RAML file, `data_types/`, and optional `interested_hooks.txt`.
3. Present the path summary. If any path is ambiguous, missing, or surprising, wait for confirmation before running scripts. If the paths are clear and complete, do not ask an extra confirmation question.
4. Run the scripts from this skill directory root in this order:
   - `python scripts/create_schemas.py`
   - `python scripts/xml_to_py.py`
   - `python scripts/link_schema_to_wbhk.py`
5. Verify that `compressed.txt`, `webhooks.jsonl`, and at least one schema file exist and are non-empty, and stop if any generated schema used the fallback generic object shape.

## Rules

- If the project has not been extracted yet, use `extract-redact-mule-jars` before this skill.
- Run this skill before reading raw Mule XML for Stage 1 analysis.
- After the scripts complete, use `compressed.txt` and `webhooks.jsonl` as the primary analysis inputs.
- Do not ask for `<PROJECT_ROOT>` again if it was already established during project selection.
- Do not run any script until ambiguous or incomplete discovered paths have been confirmed.
- If the discovered paths are clear and complete, do not require an extra confirmation turn.
- Stop immediately on missing outputs or script errors.
- Stop immediately if schema generation reported parse failures or if any generated schema contains the fallback generic object shape.
- Use the relative `scripts/...` paths from this skill directory. Do not prefix them with `.agents/skills/...`.

## Available Scripts

- `scripts/create_schemas.py` - Generates JSON Schema files from RAML `data_types/`
- `scripts/xml_to_py.py` - Produces `compressed.txt`, `webhooks.jsonl`, and scheduler seeds from Mule XML
- `scripts/link_schema_to_wbhk.py` - Enriches `webhooks.jsonl` with request and response schemas from RAML

## Reference

See `references/REFERENCE.md` for the full command blocks, path-discovery details, output interpretation, and verification steps.
