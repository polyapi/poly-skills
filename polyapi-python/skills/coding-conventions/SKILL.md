---
name: coding-conventions
description: Use when naming or renaming PolyAPI Python functions, workflow files, contexts, artefacts, or references to deployed resources.
---

# PolyAPI Python coding conventions

Read the active repository's conventions and maintained examples. Distinguish
source filename, Python entrypoint, deployed resource identity, and external SDK
identifier before changing a name; they are not interchangeable.

## Naming rules

- Use snake_case for authored Python modules, workflow directories, functions,
  and JSON artefact filenames. Choose descriptive names from the workflow or
  endpoint purpose; avoid ad-hoc abbreviations.
- Keep `polyConfig.name` aligned with the entrypoint where inline metadata is
  used. Function names and dotted context segments must be valid Python
  identifiers, not keywords. Avoid identity collisions in the same context.
- Keep project-owned contexts within the configured namespaces. Do not invent
  organization, customer, or regional prefixes for reusable examples.
- Preserve upstream API fields, OpenAPI operation IDs, generated callable names,
  generated schema filenames, and platform category names. For example,
  `CreateJobDto.schema.json`, `getRandomAdvice`, and `ai-functions` are not
  snake_case cleanup targets.
- Preserve standard documentation names and hyphenated skill folder names.
- For new related resources, keep the function, file, webhook, and trigger base
  names aligned where practical. For example, `process_event_sfx.py`,
  `process_event_hook.json`, and `process_event_trigger.json` share a clear base.
  Preserve existing deployed identities during filename-only changes.

## Recommended filename defaults

Follow explicit project conventions and discovery rules first. Where the project
has no convention for a file kind, use these defaults consistently. These are
recommended local names, not universal platform requirements or a reason to
rename existing files. A repo that uses descriptive unsuffixed JSON names can
keep that convention.

| Locally authored file | Pattern | Example |
| --- | --- | --- |
| Server function | `<name>_sfx.py` | `process_event_sfx.py` |
| Client function | `<name>_cfx.py` | `normalize_event_cfx.py` |
| Importable types module | `<name>_types.py` | `event_types.py` |
| Workflow test | `test_<behavior>.py` | `test_process_event.py` |
| Webhook artefact | `<name>_hook.json` | `process_event_hook.json` |
| Trigger artefact | `<name>_trigger.json` | `process_event_trigger.json` |
| Variable artefact | `<name>_vari.json` | `delivery_options_vari.json` |
| Job artefact | `<name>_job.json` | `replay_events_job.json` |
| Tabi artefact | `<name>_tabi.json` | `event_receipts_tabi.json` |
| OpenAPI training input | `<name>_spec.json` | `event_provider_spec.json` |
| Other authored resource JSON | `<name>.json` in its category | `event_console.json` |

Filename suffixes do not prescribe deployed resource names. Preserve the
identity fields required by the target contract and repository.

A separate `_types.py` module is appropriate only if its consumer can import or
bundle it. For a single-source-file deployer, keep runtime types inline; folder
organization does not imply packaging support.

## Rename safely

Search affected code and artefacts for the old filename and identity, excluding
secret files and SDK credential stores. Check generated calls, portable refs,
security functions, jobs/triggers, AI tools, schemas, tests, and documentation.

For a filename-only cleanup, preserve deployed identity fields and external
webhook slugs. A changed `polyConfig.name`, context, or JSON identity can create a
new resource or affect orphan detection. Treat that as an explicit migration,
including callers and dependent resources. Spec filenames may determine trained
contexts when the training command uses a `{file}` substitution.

Run the repository's discovery/reference checks and verify documentation links.
Do not deploy or delete an old resource just to finish a local rename. Use
`artefacts-usage` for ownership and `polyapi-sdk` for generated-call constraints.
