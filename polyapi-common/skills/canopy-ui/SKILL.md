---
name: canopy-ui
description: >
  Use BEFORE writing, generating, or reviewing any Canopy Application JSON —
  including collections, forms, properties, and argument mappings.
  Also use when debugging a deployment error such as "property X should not
  exist", "id must be a boolean value", or any validation failure on
  ApplicationConfig, Collection, CollectionProperty, or ArgumentMapping.
  Applies when authoring via PolyUI or when checking in UI artefacts under
  `artefacts/canopy/` alongside Tabi tables, server functions, and other
  PolyAPI workflow repo artefacts.
---

# Canopy UI (Customer Authoring)

## Overview

Canopy is a Next.js/React shell that renders itself from a single
**Application JSON** stored on a PolyAPI environment. As a customer you do
**not** fork or build Canopy; you author one JSON config and submit it through
**PolyUI** (Poly's own Canopy app at `/canopy/polyui/login`). The hierarchy
follows the public docs: **Canopy Runtime → Configured Application →
Configured Collection → Item Detail → Item Sub-page / Item Sub-collection →
Sub-item Detail**. Every dynamic value at runtime resolves to a PolyAPI
function, webhook, table, or variable that already exists in the same tenant
and environment.

## Reference files

- **`references/schema.md`** — full field-by-field reference: `CollectionProperty`,
  `ArgumentMapping`, `FunctionType` allowed keys, property types, filter
  controls, dynamic expressions, variables, templating, response config.
  Read this when authoring or debugging specific fields.
- **`references/examples.md`** — complete JSON examples: minimal skeleton,
  CRUD collection, standalone form, search pattern, filter controls, Tabi
  CRUD patterns. Read this when generating Application JSON from scratch.
- **`references/rules.md`** — generation rules and anti-patterns: CRUD-from-tables
  source-of-truth selection, collection/property/action authoring rules,
  output hygiene, common mistakes. Read this before handing off generated JSON.

## Scope

This skill applies when:

- You are **authoring or debugging a customer Canopy Application JSON** deployed via **PolyUI**.
- You are working in a **PolyAPI workflow repo** that checks in Canopy UI artefacts under an `artefacts/canopy/` directory.

When this skill is used for Canopy JSON authoring or debugging, the agent does
not need to build, prebuild, test, or otherwise run broad project verification
by default. Prefer validating the JSON shape, referenced PolyAPI resources, and
deployment-facing contract only.

It does **not** replace an explicit application contract. If this skill
conflicts with the user's request, the targeted backend artefacts, or the
declared function or table contract, follow that contract evidence and call
out the drift.

When several evidence sources disagree, use this order:

1. The user's explicit request or UI contract.
2. The targeted backend artefacts and function or table contract for the app
   you are authoring.
3. This skill's contract rules and the declared config schema.

Do not assume every field marked required in a type definition is necessarily
required for the specific application path you are authoring. Generate the
smallest internally consistent JSON that satisfies the target contract
described by this skill.

## Repo Layout (PolyAPI workflow repos)

In the workflow template used by these packs, a workflow (or utility) is typically laid out like:

- `.../src/<workflow-or-utility>/artefacts/canopy/` — Canopy Application JSON and related UI artefacts
- `.../src/<workflow-or-utility>/server/` — server functions for custom actions, orchestration, facades, or non-table behavior
- `.../src/<workflow-or-utility>/client/` — client utilities used by server functions (when applicable)
- `.../src/<workflow-or-utility>/artefacts/webhooks/`, `triggers/`, `schemas/`, `vari/`, `tabi/` — the deployed PolyAPI artefacts the UI ultimately depends on

Some repos wrap workflows under `workflows/src/...` rather than `src/...`. Use the repo's existing layout as the source of truth; the key invariant is that `artefacts/canopy/` sits alongside the workflow's `artefacts/` and optional function code.

## Alignment Rule (Canopy UI ↔ backend)

The Application JSON only **references** PolyAPI resources; it does not create them.

Before generating or changing a CRUD collection, determine which PolyAPI
resource is the intended entry point:

- First inspect the targeted backend artefacts for that app, especially Tabi
  artefacts under `artefacts/tabi/*.json` and any called server or API
  function contract.
- If the collection is simple CRUD over one Tabi table, call the table
  directly with `function.type: "query"`, the table path
  `<context>.<name>`, and operations `select`, `insert`, `update`, and
  `delete`. Do not wrap it in a server facade merely because a router or
  service function exists nearby.
- Use a server/API function for standalone actions, orchestration, validation
  beyond table constraints, cross-table workflows, side effects, custom return
  shapes, or when a maintained working Canopy app already uses that exact
  facade contract for the same domain.
- Never infer a server facade contract from source names alone. If you choose
  a facade, copy its exact argument names and operation values from a working
  Canopy example or the function contract.

When you add or change something in Canopy that calls a server/API function:

- Ensure the referenced server function exists (or is created in the same PR).
- Ensure the function's argument names and expected shape match what the Canopy JSON sends.
- If the change affects contracts, keep the relevant schemas/webhooks/triggers updated so deployed behavior stays aligned.

If you're not sure where a concept belongs (Canopy vs webhook/trigger/schema), load `polyapi-constructs` and the relevant language pack's `artefacts-usage` skill.

## Prerequisites — set up in PolyUI first

Open `https://<instance>/canopy/polyui/login` (e.g. `na1.polyapi.io`). You
need the **Use Applications** and **Manage Applications** permissions; ask
your tenant admin or `support@polyapi.io` if missing. Before any field in the
Application JSON resolves, create or confirm the following in the matching
PolyUI sidebar section:

- **Server / API / Client Functions** — referenced by their dotted context path (e.g. `myapp.orders.listOrders`).
- **Tables (Tabi)** — read the Tabi artefact's `context`, `name`, columns, primary column, required flags, and defaults. The Canopy query path is `<context>.<name>`.
- **Schemas, Webhooks, Triggers** — pick from their sections when the app calls behavior that is not simple table CRUD.
- **Variables** — Variables → Create new → Name, Context, Type, Visibility, Secrecy Level, Value.
- **Identity Providers** — under Admin, referenced by id under `login.identityProviders`.

The Application JSON only *references* these resources; it does not create them.

## Top-level shape

```jsonc
{
  "name": "My App",
  "subpath": "my-app",
  "icon": "https://…logo.svg",
  "logoSrc": "https://…logo.svg",
  "login": { "title": "…", "logoSrc": "…", "identityProviders": [] },
  "signUp": { "title": "…", "logoSrc": "…", "steps": [ … ] },
  "allowAppSwitcher": false,
  "allowEnvironmentSwitcher": false,
  "collections": [ … ],
  "forms": [ … ]
}
```

The deployed app is reachable at `/canopy/<subpath>/login`.

- `allowAppSwitcher: false` hides the app-switcher button so users cannot navigate to other Canopy applications.
- `allowEnvironmentSwitcher: false` hides the environment switcher — use when the customer should be locked to one environment.
- `description` is shown in PolyUI's app list; it does not appear in the rendered UI.
- `icon` is the application logo used in app chrome such as the sidebar.
- If you want one consistent logo everywhere, set all three: `icon`, `login.logoSrc`, and `signUp.logoSrc`.
- You may also see top-level `logoSrc` in existing configs. Treat it as optional compatibility data, not the primary branding field.
- `login.logoSrc` and `signUp.logoSrc` control the branding shown on the login and sign-up screens.

## App structure and navigation

Think of a Canopy app as a small route tree driven by JSON:

- Top-level app pages come primarily from `collections[]` and `forms[]`.
- Each collection becomes a navigable app section; `group` controls how collections are grouped in the sidebar.
- Use collection `type: "custom-page"` for a non-CRUD page that should live alongside normal collections.
- Use collection `type: "item"` for a singleton page such as Settings or Profile where there is one record rather than a list.
- Use `itemPages[]` when a user opens one record and should then be able to navigate deeper into sub-pages, sub-collections, or item-specific actions.

Common navigation patterns:

- **Sidebar sections** — define multiple entries in `collections[]`; set the same `group` value on related collections to place them under one sidebar heading.
- **Top bar controls** — the app header is mostly runtime-provided. From JSON you can mainly control whether the app switcher and environment switcher are available via `allowAppSwitcher` and `allowEnvironmentSwitcher`.
- **Standalone flows** — define pages in `forms[]` for tasks like onboarding, checkout, or one-shot operational flows.
- **Record drill-down** — open a collection item, then use `itemPages[]` to expose tabs/actions beneath that item.
- **Multi-step sign-up** — use `signUp.steps[]`; each step is its own page in the flow.

How one page leads to another:

- `response.redirect` moves the user after a form submit.
- `redirectTo` on login, sign-up submits, and function actions moves the user to another route after the function succeeds.
- `subPage` inside an item page links to another Canopy route segment.
- Query-string templating lets one page pass state into the next, e.g. `"/forms/payment?reservationId={{data.reservationId}}"`.

Useful distinction:

- There is no general-purpose `topBar` config for arbitrary custom buttons, tabs, or widgets across the whole app.
- `showSidebar`, `showHeader`, and `showBreadcrumb` control the chrome of a standalone form page.
- `allowAppSwitcher` and `allowEnvironmentSwitcher` affect the runtime header controls available for the app.
- They do **not** define navigation; the actual app/menu structure comes from `collections[]`, `forms[]`, login/sign-up routes, and item-level pages.

## Collections (quick reference)

Required: `id`, `name`, `properties`, `list`, `get`. Optional: `group`, `nameProperty`, `idProperty`, `itemActions`, `create`, `update`, `delete`, `itemPages`, `actions`.

For full field reference → **`references/schema.md`** (Collections section).  
For complete JSON examples → **`references/examples.md`**.  
For generation rules (ids, primary keys, property mapping, naming) → **`references/rules.md`**.

### Contract check (mandatory before handoff)

Before handing off any Canopy CRUD JSON, verify all of:

- **Route contract** — every route-derived identifier resolves from the same field the `get`/`update`/`delete` lookup expects.
- **Request contract** — every `arguments` entry uses a valid `ArgumentMapping` shape with exact argument names.
- **Response contract** — list functions return a flat array or paginated envelope; get/detail functions return exactly one item.
- **Property contract** — `properties` use real backend field names; `idProperty`, `nameProperty`, `list.propertyMapping` point to fields that actually exist in the returned shape.

If any contract does not line up exactly, fix the JSON before handing off.

## Argument mapping (quick reference)

| Key | Meaning |
|---|---|
| `data: true` | Whole form/item payload |
| `data: "<key>"` | One specific field |
| `id: true` | Current item's ID (boolean only — never a string or object) |
| `queryParam` | URL query parameter |
| `pathParam` | URL path parameter |
| `value` | Hard-coded constant |
| `variableId` / `variablePath` | Poly variable resolved server-side |
| `fallback` | Default when primary source is absent |
| `apiKey` / `tenant` / `environment` / `mfaToken` | Runtime context injections |

**Nothing else is valid.** For full `ArgumentMapping` and `CollectionProperty` allowed-keys tables → **`references/schema.md`** (Strictly validated field reference).

## Choosing functions

- For table-backed CRUD: `function.type: "query"` with `operation: select/insert/update/delete` against `<context>.<tableName>`.
- Use a **server function** for orchestration, validation beyond table constraints, cross-table workflows, side effects, or custom return shapes.
- **Never point Canopy at a `client` function.** Check the function's `polyConfig` in source: if its type is `PolyClientFunction`, it cannot be called from Canopy. Only `PolyServerFunction` (and equivalent API/query functions) are valid Canopy targets.
- Choose the entry point from the actual backend contract. If the targeted CRUD path is simple direct table CRUD, generate direct Tabi queries. If the targeted path is a facade/router, reuse that exact facade contract. Do not choose a facade only because one exists in `server/`, and do not bypass a required facade by pointing at internal client functions.

## Deploy via PolyUI

1. PolyUI → **Applications** → existing app → **Update**, or → **+ Create**.
2. Fill **Name**, **Description**, **Visibility** (`Environment` / `Tenant` / `Public`), and paste the full Application JSON into **Config**.
3. Submit. The deployed app is at `/canopy/<subpath>/login`. The API key shown in the header (for example, *Alice — Production — Developer Key*) determines the tenant and environment where the change lands; referenced functions and variables must exist in that scope.

CI / integrators may automate via `PUT /applications/{id}/config`, but the customer workflow is UI-only.
