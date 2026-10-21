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
  and JSON artefact filenames. Use `_sfx.py` / `_cfx.py` for deployable files when
  those are the repository's discovery conventions, and `test_<behavior>.py` for
  tests.
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
- Artefact suffixes such as `_hook`, `_trigger`, `_vari`, `_job`, and `_tabi` are
  useful conventions, not universal platform requirements. Follow the target
  repo; category directories already identify the resource kind.

| Locally authored file | Example |
| --- | --- |
| Server function | `process_event_sfx.py` |
| Client function | `fetch_advice_cfx.py` |
| Workflow test | `test_process_event.py` |
| Webhook artefact | `motd_hook.json` |
| Variable artefact | `service_config.json` |

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
