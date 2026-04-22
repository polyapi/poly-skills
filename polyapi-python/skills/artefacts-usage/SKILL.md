---
name: artefacts-usage
description: Defines generic PolyAPI artefact structures, folder layout, and field rules. Use before creating webhook, trigger, variable, job, tabi, or workflow artefact files.
---

# Skill: Artefacts Usage

## Purpose

Define the correct structure, field requirements, and placement for PolyAPI JSON artefacts, plus the baseline folder layout for workflows and shared utilities.

## When to use

Load this skill before creating any artefact JSON file, before laying out a new workflow or shared utility folder, or when reviewing generated artefacts for structural compliance.

---

## Rules

- One webhook JSON per public endpoint — never collapse multiple endpoints into one generic webhook.
- Do not create `/console/*` endpoints unless the user explicitly asks.
- Every webhook must have an explicit subpath — never use a catch-all pattern for new migration work.
- Keep one workflow per `src/<workflow_name>/` folder.
- Put shared reusable implementations under `src/utilities/<utility_name>/`.
- Keep `scripts/` folders one-off and local; do not treat them as shared runtime dependencies.
- Job `id` fields are left empty until deployment; note this as a post-deployment step.
- Never embed secret values in artefact files — record names only.

## Minimum checklist

- Follow the required workflow folder layout under `src/<workflow_name>/`.
- Follow the shared utility layout under `src/utilities/<utility_name>/` when code is reused across workflows.
- Use `snake_case` for all Python files and JSON artefact files.
- Create one webhook JSON per public endpoint.
- Add a paired trigger JSON when the target repo checks in trigger artefacts for public endpoints.
- Preserve Mule status codes and explicit request and response schemas.
- Use secret variables for passwords, tokens, and API keys.
- Treat XML handling as an explicit webhook boundary concern.

## Reference

See `./references/REFERENCE.md` for the folder trees, JSON examples, field rules, XML parser options, job and variable examples, and `OVERVIEW.md` expectations.
