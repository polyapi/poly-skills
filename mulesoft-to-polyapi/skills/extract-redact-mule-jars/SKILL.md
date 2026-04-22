---
name: extract-redact-mule-jars
description: Extracts and redacts Mule application jars under `jars/` into sanitized top-level project folders. Use when a project exists only as packaged jars and the user confirms extraction, before running `compress-source`, when one integration jar needs to be unpacked on demand, or when existing extracted projects only need configuration redaction refreshed without unpacking again.
compatibility: Requires `bash`, `unzip`, `python3`, local access to the repo root, and Mule jars under `jars/` or existing extracted project folders.
---

# Skill: extract-redact-mule-jars

Prepares Mule projects for analysis by unpacking jars and redacting sensitive configuration values.

Use this skill before `compress-source` when the source project is not yet available as an extracted folder.

## Workflow

1. Determine whether the target project already exists as an extracted top-level folder.
2. If folder and jar names do not match exactly, look for close matches before assuming the project is missing.
3. Treat differences such as underscores versus hyphens, `gha-` prefixes, build suffixes, version formatting, or manual renames as possible matches.
4. If one or more close matches exist, show the candidate folder and jar names and ask the user to confirm whether they refer to the same integration.
5. If the project exists only as a jar under `jars/`, tell the user that extraction will overwrite any matching extracted project folder and that extraction also performs redaction.
6. Before unjarring any file, get explicit user confirmation. Do not unpack jars automatically.
7. From the `mulesoft-to-polyapi` pack root, run one of:
   - `./skills/extract-redact-mule-jars/scripts/extract_redact_mule_jars.sh` to extract all jars under `jars/` and redact each extracted project
   - `./skills/extract-redact-mule-jars/scripts/extract_redact_mule_jars.sh <jar_or_project>` to extract just one integration by jar filename, jar stem, or derived project folder name, then redact it
   - `./skills/extract-redact-mule-jars/scripts/extract_redact_mule_jars.sh --redact-only [project_dir ...]` to re-sanitize existing extracted folders without unpacking jars
8. Use `--redact-only` when the user already unpacked the project manually or when only sanitization needs to be refreshed.
9. Verify that the expected top-level project folder exists and that `configuration-*.yaml` files have sensitive values replaced with `[REDACTED]`.
10. Only after extraction or redaction succeeds, continue with `compress-source` or deeper Mule analysis.

## Rules

- Run this skill from the `mulesoft-to-polyapi` pack root.
- Do not reimplement jar extraction in Python or another script; use `./skills/extract-redact-mule-jars/scripts/extract_redact_mule_jars.sh`.
- Extraction always performs redaction on the extracted project immediately afterward.
- Do not unjar any file until the user explicitly confirms that extraction should happen.
- Do not assume a project is missing just because the folder name and jar name are not identical. Compare close candidates and ask the user to confirm.
- Prefer targeted extraction when the user wants a single integration analysed; do not unpack every jar unless the user asked for that or the task genuinely requires all projects.
- Full extraction deletes and recreates target extracted folders. If a matching folder already exists and may contain user edits or generated artefacts, confirm before rerunning extraction.
- Use `--redact-only` when the project is already extracted, when the user manually unjared it, or when only configuration sanitization needs to be refreshed.
- Treat the extracted top-level project folder as the working source tree for later skills.

## Reference

See `references/REFERENCE.md` for command examples, verification steps, and output expectations.
