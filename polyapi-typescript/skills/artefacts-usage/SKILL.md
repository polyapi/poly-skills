---
name: artefacts-usage
description: Use before creating or changing PolyAPI TypeScript artifact JSON, workflow layout, or webhook and trigger wiring and the task needs concrete rules for artifacts, folders, and runtime alignment.
---

# TypeScript Artefacts Usage

## Overview

This skill defines the expected structure and placement of PolyAPI artifacts in
TypeScript repos, plus the minimum alignment rules between TypeScript
entrypoints, generated platform types, JSON artifacts, and tests.

The local [`references/REFERENCE.md`](./references/REFERENCE.md) file contains
the fuller folder tree, artifact map, and Maybourne-style examples behind these
rules.

## When to Use

- Creating or editing `artifacts/` JSON in a TypeScript PolyAPI repo
- Adding a new workflow or utility under `src/`
- Wiring a webhook to a server function
- Deciding whether something belongs in `vari`, `tabi`, `jobs`, `schemas`,
  `specs`, or `canopy`
- Reviewing whether TypeScript, artifacts, and tests still describe the same
  deployed behavior

Do not use this skill:
- For pure TypeScript style questions with no artifact or layout change
- When a repo has stronger local workflow docs that intentionally override
  these defaults

## Quick Reference

- Keep one workflow per `src/<workflow>/` folder.
- Keep `artifacts/`, `client/`, `server/`, and `types/` together under the
  same workflow.
- Put genuinely shared reusable code under `src/utilities/`.
- Use `https://eu1.polyapi.io/swagger-json` as the source of truth for the
  JSON field shape of platform-managed artefacts. Use this skill for repo
  layout, naming, and workflow alignment.
- Standard artifact directories are `schemas/`, `specs/`, `webhooks/`,
  `triggers/`, `vari/`, `tabi/`, `jobs/`, and optional `canopy/`.
- Keep deployed names and contexts aligned across the TypeScript entrypoint,
  inline metadata or function JSON, webhook artifact, and trigger artifact.
- One public endpoint should map to one explicit webhook artifact.
- When a webhook calls code, add or update the matching trigger in the same
  change.
- Use `vari` for config, secrets, retry policies, token caches, and other
  runtime configuration.
- Use `tabi` for persisted workflow state, lookup tables, and idempotency or
  routing data that must survive individual executions.
- Use `jobs` for scheduled cleanup and maintenance, especially around `tabi`
  retention and lifecycle tasks.
- Keep TypeScript, JSON artifacts, and tests aligned in the same PR.

## Implementation

Follow [`references/REFERENCE.md`](./references/REFERENCE.md). For exact naming
and coding style within `.ts` files, also use
[`../coding-conventions/SKILL.md`](../coding-conventions/SKILL.md). For runtime
tooling and sync expectations, also use
[`../polyapi-sdk/SKILL.md`](../polyapi-sdk/SKILL.md).

## Common Mistakes

- Updating `server/*.ts` or `client/*.ts` but forgetting the matching webhook,
  trigger, or schema change
- Treating runtime workflow state as `vari` config when it should be modeled in
  `tabi`
- Creating a catch-all webhook instead of one explicit endpoint contract
- Scattering shared logic across workflow folders instead of `src/utilities/`
- Treating `canopy/` as mandatory when the repo does not actually use Canopy
