---
name: canopy-config-ui-runtime
description: Use when changing Canopy collection config, filters, fields, action placement/visibility, dynamic properties, generic React rendering, execute-function pages, collection CRUD execution, or PolyAPI runtime request mapping.
---

# Canopy Config, UI, and Runtime

## Overview

Canopy UI is config-driven, but config is only one layer. Collection behavior
usually depends on:

- `collection.json` for UI mapping and rendering.
- `api.json` for PolyAPI function/gateway contract.
- `src/api/poly/function.ts` for runtime request construction.
- `src/api/poly/collection.ts` for list/get/create/update/delete orchestration.
- `src/api/poly/page.ts` (`submitPage`) for item subpage / execute / webhook
  page submissions.
- `src/api/poly/webhook.ts` (`triggerWebhookHandle`) for direct webhook trigger
  routes.
- Generic collection/action React components for display and interaction.

It also covers execute-function, trigger-webhook, configured forms
(`src/app/[appId]/forms/[formId]`), and collection execution flows.

## Quick Rules

- Inspect `collection.json` and sibling `api.json` together for the
  collection that matches the URL segment
  (`/<appId>/collections/<collection>/...`). All collection folders under
  `polyapi_config/collections/` are equally important; list the directory and
  pick the right one(s).
- Prefer config changes before React changes when supported.
- Do not copy fields between similar config surfaces without checking schema
  validity.
- Optional empty filters and request values should be omitted when the backend
  expects absence.
- Use explicit property `type`; runtime object values do not imply JSON UI.
- Use `readOnly: true` for display-only fields following local config patterns.
- Keep action placement/visibility config-driven when the generic action system
  supports it.
- Keep generic route TSX files generic.
- For larger or logic-heavy UI additions, extract child components as render
  boundaries.
- Use `src/api/poly/function.ts` as the canonical execution reference before
  copying inline `collection.ts` switch blocks.
- For raw functions with MFA, route MFA through the raw header path as well as
  any configured body mapping.

## Workflow

1. Locate the relevant directory under `polyapi_config/collections`.
2. Read `collection.json` for UI properties, filters, actions, and mapping.
3. Read `api.json` for gateway URL, arguments, validation, and omission rules.
4. If the issue involves runtime values, inspect `getExecutionBody` and function
   dispatch in `src/api/poly/function.ts`.
5. If the issue involves list/get/create/update/delete, inspect the relevant
   call path in `src/api/poly/collection.ts`.
6. If UI code is required, read the generic component that owns the behavior
   before editing.
7. For execute-function pages, preserve hidden form/parser contracts such as
   `PolyVariable::`.
8. Validate JSON and run targeted diagnostics.

## Common Mistakes

- Editing React before checking config.
- Updating `collection.json` but forgetting `api.json`.
- Sending `status=` or other empty optional values.
- Assuming function gateway logs prove the final backend REST URL.
- Assuming `dynamic.readOnly` support means actions support the same expression
  system.
- Changing `ActionBarMenu` delete behavior during unrelated action work.
- Copying `collection.ts` raw execution blocks without checking
  `executeFunction`.
- Adding `React.memo`, `useMemo`, or `useCallback` as style instead of need.

## Reference

See [references/REFERENCE.md](./references/REFERENCE.md) for config examples,
runtime execution details, action behavior, React boundaries, and execute-page
contracts.

