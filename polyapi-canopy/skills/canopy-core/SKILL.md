---
name: canopy-core
description: Use when onboarding to the Canopy repo, mapping source ownership, choosing a source of truth, planning cross-layer Canopy work, or handling PolyUI config deployment requirements.
---

# Canopy Core

## Overview

Canopy is a Next.js/React shell rendered from PolyAPI application config. Most
meaningful changes cross at least two layers: checked-in JSON config,
server-side request construction, generic collection rendering, auth/session
state, or PolyAPI deployment.

Use this skill first when you need the repo map, source-of-truth order, or
deployment implications. Detailed file ownership and workflow notes are in the
local [reference](./references/REFERENCE.md).

## Quick Rules

- Follow checked-in implementation before older notes, README, or framework guesses.
- Inspect `polyapi_config/collections/<collection>/collection.json` and the
  sibling `api.json` for collection-backed work. `<collection>` is the folder
  name and matches the URL segment
  (`/<appId>/collections/<collection>/...`). All collection folders under
  `polyapi_config/collections/` are equally important — list the directory
  and pick the one(s) that match the URL or feature.
- Prefer config changes before React/TypeScript changes when config is the
  intended source of truth.
- Keep generic collection pages generic; avoid hardcoded collection/action logic
  in route TSX.
- Reuse existing helpers and patterns before adding abstractions.
- Keep frontend config, runtime request construction, backend validation, and
  rendered UI aligned.
- Any merged `collection.json` or associated `api.json` change requires the
  manual PolyUI config deployment workflow targeting `develop`.

## Workflow

1. Classify the task: config, rendering, request construction, auth/security,
   or deployment.
2. Start with the relevant checked-in implementation and config files.
3. Use local references as supporting context where the current branch differs.
4. Build a small file map before editing.
5. Verify role/security and deployment implications before finishing.
6. If collection config changed, mention the manual workflow requirement.

## Common Mistakes

- Treating Canopy as a normal page-by-page React app instead of a config-driven
  shell.
- Reading only README/examples and missing current implementation.
- Updating collection config without considering the sibling API spec.
- Forgetting `all_collections.js` when adding or removing a collection.
- Merging config changes without the required PolyUI app config deployment.

## Reference

See [references/REFERENCE.md](./references/REFERENCE.md) for the source map,
source-of-truth order, deployment workflow, and known documentation drift.

