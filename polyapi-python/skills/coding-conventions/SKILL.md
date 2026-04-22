---
name: coding-conventions
description: Defines PolyAPI Python naming and file-layout conventions for functions, artefacts, and related files. Use before naming or reviewing Python migration artefacts.
---

# Skill: Python Coding Conventions

## Purpose

Define reusable Python naming and file-layout rules for PolyAPI artefacts
without baking in project-specific namespaces, slug tokens, or credential
schemes.

## When to use

Use this skill before naming Python functions, webhooks, triggers, variables,
tabis, jobs, or related files. If the target repo has a project-specific
standards skill, load that as an overlay.

---

## Core rules

- Use `snake_case` for Python files, JSON artefact files, and artefact base names.
- Keep deployed names deterministic and readable; derive them from the workflow or endpoint purpose instead of ad-hoc abbreviations.
- Do not create duplicate deployed names in the same context or duplicate entrypoints that will collide in the generated SDK or runtime.
- Context segments and function names must be valid identifiers. Do not use Python keywords as names or context segments.

---

## File naming (Python)

| Artefact type | File suffix | Example |
|---|---|---|
| Server function | `_sfx.py` | `get_member_balance_sfx.py` |
| Client function | `_cfx.py` | `sdk_call_with_retry_cfx.py` |
| Types file | `_types.py` | `member_info_types.py` |
| Webhook artefact | `_hook.json` | `get_member_balance_hook.json` |
| Trigger artefact | `_trigger.json` | `get_member_balance_trigger.json` |
| Variable artefact | `_vari.json` | `currency_config_vari.json` |
| Job artefact | `_job.json` | `sync_rates_job.json` |
| Tabi artefact | `_tabi.json` | `currency_map_tabi.json` |

All Python files use `snake_case`. All JSON artefact file names use `snake_case`.

---

## Rules

- Never use camelCase for Python files or artefact file names.
- Keep the deployed function name, file base name, and artefact base name aligned where practical.
- For project-specific namespace families, slug tokens, logger contexts, credential namespaces, or webhook/trigger pairing rules, follow the active repo's standards overlay.
