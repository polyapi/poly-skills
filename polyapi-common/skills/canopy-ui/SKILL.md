---
name: canopy-ui
description: Use when authoring or debugging Canopy Application JSON in PolyUI or in a PolyAPI workflow repo that checks in UI artefacts under `artefacts/canopy/` alongside `server/` functions.
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

## Scope

This skill applies when:

- You are **authoring or debugging a customer Canopy Application JSON** deployed via **PolyUI**.
- You are working in a **PolyAPI workflow repo** that checks in Canopy UI artefacts under an `artefacts/canopy/` directory.

It does **not** replace checked-in implementation. If this skill conflicts with the target repo’s code or artefacts, follow the checked-in implementation and call out the drift.

## Repo Layout (PolyAPI workflow repos)

In the workflow template used by these packs, a workflow (or utility) is typically laid out like:

- `.../src/<workflow-or-utility>/artefacts/canopy/` — Canopy Application JSON and related UI artefacts
- `.../src/<workflow-or-utility>/server/` — server functions that implement the backend behavior the Canopy app calls
- `.../src/<workflow-or-utility>/client/` — client utilities used by server functions (when applicable)
- `.../src/<workflow-or-utility>/artefacts/webhooks/`, `triggers/`, `schemas/`, `vari/`, `tabi/` — the deployed PolyAPI artefacts the UI ultimately depends on

Some repos wrap workflows under `workflows/src/...` rather than `src/...`. Use the repo’s existing layout as the source of truth; the key invariant is that `artefacts/canopy/` sits alongside the workflow’s `server/` code.

## Alignment Rule (Canopy UI ↔ backend)

The Application JSON only **references** PolyAPI resources; it does not create them.

So when you add or change something in Canopy that calls a function:

- Ensure the referenced server function exists (or is created in the same PR).
- Ensure the function’s argument names and expected shape match what the Canopy JSON sends.
- If the change affects contracts, keep the relevant schemas/webhooks/triggers updated so deployed behavior stays aligned.

If you’re not sure where a concept belongs (Canopy vs webhook/trigger/schema), load `polyapi-constructs` and the relevant language pack’s `artefacts-usage` skill.

## Prerequisites — set up in PolyUI first

Open `https://<instance>/canopy/polyui/login` (e.g. `na1.polyapi.io`). You
need the **Use Applications** and **Manage Applications** permissions; ask
your tenant admin or `support@polyapi.io` if missing. Before any field in the
Application JSON resolves, create or confirm the following in the matching
PolyUI sidebar section:

- **Server / API / Client Functions** — referenced by their dotted context
  path (e.g. `myapp.orders.listOrders`, `myapp.payments.applyPayment`).
  Functions are typically deployed by an integrator with `poly function add`.
- **Schemas, Webhooks, Triggers, Tables (Tabi)** — pick from their sections.
- **Variables** — Variables → Create new → Name, Context, Type, Visibility,
  Secrecy Level, Value.
- **Identity Providers** — under Admin, referenced by id under
  `login.identityProviders`.

The Application JSON only *references* these resources; it does not create
them.

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

- `allowAppSwitcher: false` hides the app-switcher button in the top bar so
  users cannot navigate to other Canopy applications they have access to.
- `allowEnvironmentSwitcher: false` hides the environment switcher — use
  this when the customer should be locked to one environment.
- `description` is shown in PolyUI's app list; it does not appear in the
  rendered UI.
- `icon` is the application logo used in app chrome such as the sidebar.
- If you want one consistent logo everywhere, set all three: `icon`,
  `login.logoSrc`, and `signUp.logoSrc`.
- You may also see top-level `logoSrc` in existing configs. Treat it as
  optional compatibility data, not the primary branding field.
- `login.logoSrc` and `signUp.logoSrc` control the branding shown on the
  login and sign-up screens.

## Minimal working skeleton

The JSON below is a complete, deployable application with one CRUD collection
and one standalone form. It can be used as a starting point. Replace the function paths, properties, and branding with your own ones.

```jsonc
{
  "name": "My App",
  "subpath": "my-app",
  "icon": "https://example.com/logo.svg",
  "login": {
    "title": "My App Login",
    "logoSrc": "https://example.com/logo.svg",
    "allowPolyApiKey": true
  },
  "allowAppSwitcher": false,
  "allowEnvironmentSwitcher": false,

  // ── CRUD collection: a list of records the user can view, create, and edit ──
  "collections": [
    {
      "id": "orders",
      "name": "Orders",
      "group": "Operations",          // sidebar section heading (optional)
      "nameProperty": "orderNumber",  // which field becomes the card title

      // Fields shown in list cards, detail view, create/edit forms
      "properties": {
        "id":          { "label": "ID",           "type": "text",   "readOnly": true,
                         "excludeFromCreate": true, "excludeFromUpdate": true },
        "orderNumber": { "label": "Order Number", "type": "text" },
        "status":      { "label": "Status",       "type": "enum",
                         "values": [{ "name": "Open", "value": "OPEN" },
                                    { "name": "Closed", "value": "CLOSED" }] },
        "amount":      { "label": "Amount",       "type": "number", "step": 0.01 }
      },

      "itemActions": ["get", "create", "update"],   // which CRUD buttons appear

      "list": {
        "paginated": true,
        "function": {
          "path": "myapp.orders.list",    // replace with your function path
          "type": "server",
          "arguments": {
            "page": { "queryParam": "page", "fallback": { "data": 1 } }
          }
        }
      },
      "get": {
        "function": {
          "path": "myapp.orders.getById",
          "type": "server",
          "arguments": { "id": { "id": true } }
        }
      },
      "create": {
        "actionLabel": "New Order",
        "function": {
          "path": "myapp.orders.create",
          "type": "server",
          "arguments": { "order": { "data": true } }   // send the whole form as "order"
        }
      },
      "update": {
        "submitMode": "changed",        // only send fields the user actually changed
        "function": {
          "path": "myapp.orders.update",
          "type": "server",
          "arguments": { "orderId": { "id": true }, "order": { "data": true } }
        }
      }
    }
  ],

  // ── Standalone form: a one-off action not tied to a list ──
  "forms": [
    {
      "id": "send-confirmation",
      "title": "Send Confirmation",
      "subpath": "send-confirmation",
      "showSidebar": false,
      "showHeader": false,
      "cancel": false,

      // Optionally pre-fill fields from a function before the user sees the form
      "prepare": {
        "function": {
          "path": "myapp.orders.getById",
          "type": "server",
          "arguments": { "id": { "queryParam": { "key": "orderId", "type": "text" } } }
        }
      },

      "properties": {
        "orderNumber": { "label": "Order Number", "type": "text", "readOnly": true },
        "email":       { "label": "Recipient Email", "type": "text", "required": true }
      },

      "submit": {
        "label": "Send",
        "icon": "send",
        "variant": "primary",
        "location": "bottom",
        "function": {
          "path": "myapp.orders.sendConfirmation",
          "type": "server",
          "arguments": {
            "orderId":  { "queryParam": { "key": "orderId",  "type": "text" } },
            "posId":  { "queryParam": { "key": "posId",  "type": "text" } },
            "email":    { "data": "email" }   // send just the one editable field from the form
          }
        }
      },

      "response": {
        "type": "confirmation",
        "confirmation": {
          "title": "Done",
          "message": "Confirmation sent successfully."
        }
      }
    }
  ]
}
```

The names used above (`myapp.orders.*`, `orderId`, `posId`, `email`) are illustrative — use the actual function paths, argument names, and field names that match your integration.

## App structure and navigation

Think of a Canopy app as a small route tree driven by JSON:

- Top-level app pages come primarily from `collections[]` and `forms[]`.
- Each collection becomes a navigable app section; `group` controls how
  collections are grouped in the sidebar.
- Use collection `type: "custom-page"` for a non-CRUD page that should live
  alongside normal collections in the app navigation.
- Use collection `type: "item"` for a singleton page such as Settings or
  Profile where there is one record rather than a list.
- Use `itemPages[]` when a user opens one record and should then be able to
  navigate deeper into sub-pages, sub-collections, or item-specific actions.

Common navigation patterns:

- **Sidebar sections** — define multiple entries in `collections[]`; set the
  same `group` value on related collections to place them under one sidebar
  heading.
- **Top bar controls** — the app header is mostly runtime-provided. From JSON
  you can mainly control whether the app switcher and environment switcher are
  available via `allowAppSwitcher` and `allowEnvironmentSwitcher`.
- **Standalone flows** — define pages in `forms[]` for tasks like onboarding,
  checkout, or one-shot operational flows.
- **Record drill-down** — open a collection item, then use `itemPages[]` to
  expose tabs/actions beneath that item.
- **Multi-step sign-up** — use `signUp.steps[]`; each step is its own page in
  the flow.

How one page leads to another:

- `response.redirect` moves the user after a form submit.
- `redirectTo` on login, sign-up submits, and function actions moves the user
  to another route after the function succeeds.
- `subPage` inside an item page links to another Canopy route segment.
- Query-string templating lets one page pass state into the next, for example
  `"/forms/payment?reservationId={{data.reservationId}}"`.

Useful distinction:

- There is no general-purpose `topBar` config for arbitrary custom buttons,
  tabs, or widgets across the whole app.
- `showSidebar`, `showHeader`, and `showBreadcrumb` control the chrome of a
  standalone form page.
- `allowAppSwitcher` and `allowEnvironmentSwitcher` affect the runtime header
  controls available for the app.
- They do **not** define navigation; the actual app/menu structure comes from
  `collections[]`, `forms[]`, login/sign-up routes, and item-level pages.

## Collections

A collection is a CRUD-backed list. Required: `id`, `name`, `properties`,
`list`, `get`. Optional: `group`, `nameProperty`, `itemActions`, `create`,
`update`, `delete`, sub-pages, sub-collections.

Collections come in three `type` flavours:

- **`items`** (default — the standard list of records described below).
- **`item`** (singleton) — one record, no list view. Use for "settings"-
  style screens. Provide `get` and optionally `update`; no `list`/`create`/
  `delete`.
- **`custom-page`** — a static page rendered from `elements[]`
  (`{ elementType: "text" | "field" }`) with optional `dataFunction` to
  pre-load values. Use for dashboards or info pages that aren't a list.

Extra collection-level attributes for the default `items` type:

- `idProperty` — which property holds the row id; defaults to `"id"`.
- `nameProperty` / `descriptionProperty` — which fields supply the card
  title and subtitle; default to `"name"` / `"description"`.
- `description` — short blurb shown above the list.
- `propertyMode: "manual" | "auto"` — `auto` lets Canopy infer extra
  columns from the `list` response when the explicit `properties` map
  doesn't cover every key.
- `inferredProperties` — hints applied to auto-inferred properties
  (label/type per key).
- `hiddenProperties` — array of property keys to hide everywhere; useful
  alongside `propertyMode: "auto"`.
- `actions` — collection-level extra buttons (see Actions and placement).
- `itemPages` — sub-pages, sub-collections, and one-shot action pages
  attached to each item (see Item pages).

```jsonc
{
  "id": "tasks", "name": "Tasks", "group": "Dashboard",
  "nameProperty": "title",
  "properties": {
    "id":     { "label": "ID", "readOnly": true,
                "excludeFromCreate": true, "excludeFromUpdate": true },
    "title":  { "label": "Title", "type": "text" },
    "status": { "label": "Status", "type": "enum",
                "values": [{ "name": "To Do", "value": "TODO" }, …] }
  },
  "itemActions": ["get", "update", "create"],
  "list":   { "function": { "path": "dashboard.listTasks",   "type": "server" },
              "propertyMapping": { "id": "id", "name": "title",
                                   "description": "status" },
              "paginated": true },
  "get":    { "function": { "path": "dashboard.getTask",     "type": "server",
                            "arguments": { "id": { "id": true } } } },
  "create": { "actionLabel": "Add", "submitLabel": "Save",
              "function": { "path": "dashboard.createTask", "type": "server",
                            "arguments": { "body": { "data": true } } } },
  "update": { "function": { "path": "dashboard.updateTask", "type": "server",
                            "arguments": { "id": { "id": true },
                                           "body": { "data": true } } },
              "submitMode": "changed" },
  "delete": { "confirmTitle": "Delete task?",
              "confirmText": "This cannot be undone.",
              "function": { "path": "dashboard.deleteTask", "type": "server",
                            "arguments": { "id": { "id": true } } } }
}
```

`list.propertyMapping` maps row fields to the standard `id` / `name` /
`description` slots so cards render consistently. Add `paginated: true`
plus `page` and `pageSize` `queryParam` arguments for paginated APIs.

CRUD action options:

- `actionLabel` / `submitLabel` / `cancelLabel` — button text overrides.
- `create.submitMode: "all" | "filled"` — send all fields or only
  non-empty fields on Create.
- `update.submitMode: "all" | "changed" | "filled"` — send all fields,
  only changed fields, or only non-empty fields on Update. `"changed"`
  is the most common Update setting and avoids overwriting fields the user
  didn't touch.
- `placement: "primary" | "secondary" | "menu"` and `menuOrder` —
  position of Update/Delete relative to other actions.
- `delete.confirmTitle` / `confirmText` — confirmation modal copy.
- `create.responseForm` — see Response config below.
- `mfaSupported: true` and `mfaRequiredActionsKey` — enable per-action
  MFA gating (see MFA gating).

## Properties

Supported `type` values: `text`, `multiline`, `number`, `boolean`, `enum`,
`multi`, `nested`, `array`, `json`, `code`, `checkbox`, `link`, `picker`,
`legalCheckbox`, `date`, `time`, `datetime`, `variable`. Number properties
also accept:

- `min` / `max` — lower and upper bounds enforced in the UI.
- `step` — allowed increment and implied precision. `step: 0.01` means the
  input accepts hundredths (`25.01`) but rejects thousandths (`25.001`).
  Common values: `1` for whole numbers, `0.01` for monetary amounts, `0.001`
  for quantities with three decimal places.
- `units` — label suffix shown after the input (e.g. `"kg"`, `"USD"`).

Multiline properties accept `autoSize`, `minRows`, `maxRows`.

Date / time / datetime properties accept:

- `min` / `max` — ISO strings; bound the picker.
- `dateStyle: "full" | "long" | "medium" | "short"` — format used in
  detail views.
- `timeStyle` (same enum) — format used for `time` and `datetime`.
- `hourCycle: "h12" | "h24"` — 12-hour vs 24-hour clock.
- `inputTimeZone` / `outputTimeZone` — IANA time-zone names
  (e.g. `"America/Los_Angeles"`); separate so the user enters values in
  one zone but the function receives them in another.

Enum-style properties (`enum`, plus the picker variants) accept:

- `values` — fixed `[{ name, value, readOnly? }, …]`.
- `functionValues` — `{ function, valueKey?, nameKey? }`; defaults
  `valueKey: "id"`, `nameKey: "name"`.
- `defaultValues` — array of `ArgumentMapping` entries, used to call
  `functionValues.function` with arguments derived from the current
  context.
- `queryParam` — bind the field to a URL query parameter so changing it
  updates the URL (and is restorable from the URL).
- `allowEmpty: true` — add a blank option.
- `showValue: true` — display the underlying `value` next to the
  human-readable `name` in the dropdown.

Layout / link hints (any property type):

- `flex: true` — let the field share a row with its siblings instead of
  taking a full row.
- `inset: true` — indent the field as part of a logical group.
- `href` / `target` — make the property render as a link (paired with
  `type: "link"`); both fields support templating.

Picker properties (`type: "picker"`) wrap an enum-style chooser around a
rich list backed by a function:

- `pickerName` / `pickerLabel` — modal title / button label.
- `pickerValues: [{ name, function, valueKey?, nameKey? }, …]` — multiple
  named tabs each backed by a different function.
- `itemType: "text" | "number"` — the type of the value the picker
  ultimately writes back into the form.

Variable properties (`type: "variable"`) let the user pick a Poly variable
as the value of the field:

- `variableType` — the underlying value type (any property type except
  `array`, `nested`, `multi`, `variable`).
- `asReference: true` — store the variable as a `{ type: "PolyVariable",
  id }` reference instead of resolving it client-side.

Legal-checkbox properties (`type: "legalCheckbox"`) render a terms-of-
service tick-box:

- `orgName` — organisation displayed in the agreement text.
- `url` — link to the legal document.
- `requiredError` — message shown when the user submits without ticking.

Nested and array shapes:

- **`type: "nested"`** — group of sub-fields. Has its own `properties` map
  and renders as an inset block. Supports `expandable: true | "<label>"`
  to collapse the block by default.
- **`type: "array"`** — a repeatable group. `items` is
  `{ "type": "nested", "properties": { … } }` describing the per-row
  fields. Optional: `canAddItems: true`, `canRemoveItems: true`,
  `pagination: true`, `itemLabelProperty` — which inner property supplies
  the row's collapsed-state label.
- **`type: "multi"`** — a single field that accepts several `FieldType`s
  (`string` | `number` | `boolean` | `object`) selected via a small switch.

Code and JSON properties:

- `type: "code"` requires `language` (e.g. `"javascript"`, `"sql"`,
  `"yaml"`) and accepts `hideLanguage: true` to hide the language picker.
- `type: "json"` accepts `hideLanguage: true` likewise.

Property definitions describe the field's type, label, validation, and UI
behavior; they do not create the runtime value by themselves. On collection
pages, a field's value comes from the current item returned by the list
function or, more commonly for detail/edit, the get function. On Create and
standalone forms, the initial value comes from `defaultValue` and may be
overridden by the prepare function when that form uses one.

Property attributes (all optional):

- `label` — display name shown above the field and in list headers.
- `placeholder` — placeholder text shown in empty inputs.
- `helperText` / `description` — helper text rendered under the input.
- `tooltip` — `{ title, value, url?, action? }` for an `(i)` tooltip next to
  the label.
- `defaultValue` — initial value when the field is first rendered (used by
  Create forms and standalone forms before `prepare` returns).
- `required: true` — fail submit if the field is empty. Pair with
  `requiredError` to customise the message.
- `values` — fixed enum options `[{ name, value }, …]`. Use with
  `type: "enum"`. Each option may itself be `readOnly: true`.
- `functionValues` — `{ function, valueKey?, nameKey? }`; the function's
  result populates enum options at runtime (dynamic dropdown).
- `key: true` — use this property as the lookup key for CRUD instead of the
  default `id`.

Visibility / form-membership flags — these decide whether the field shows up
at all in each context. **`excludeFrom*` removes the field entirely from
that view; the user does not see it and cannot enter it. Use this (not
`readOnly`) for values that should be invisible in a given form.**

- `readOnly: true` — field is rendered but disabled. The user can see the
  current value but cannot change it. The value is still submitted.
- `excludeFromCreate: true` — the field is **not rendered** in the **Create**
  form at all. Use for server-assigned values (`id`, `createdAt`, audit
  fields) that the user should not enter.
- `excludeFromUpdate: true` — the field is **not rendered** in the
  **Edit / Update** form. Use for values that are valid at creation but must
  not change afterwards (`id`, foreign keys, `createdAt`).
- `excludeFromDetail: true` — the field is **not rendered** on the
  **detail** page (read-only view). Use for housekeeping values that the
  user never needs to inspect.
- `excludeFromSubmit: true` — the field renders, but its value is **not
  included in the submit payload**. Use for purely informational fields or
  values driven entirely by other arguments.
- `hidden: true` — the field is **never rendered** in any form or detail
  view. Its value remains addressable from argument mapping via `data`.
- `hideLabel: true` — render the input without its label.
- `hideIfEmpty: true` — on the **detail** view only, hide the property when
  its value is null/empty so the layout stays clean.
- `hideOnCreate: true` — hide the field in the **Create** form only (the
  field still appears in Update and detail). Similar to `excludeFromCreate`
  but may still submit the value.
- `visibleOnCard: true` — surface this property on the collection list card
  (in addition to the standard `id` / `name` / `description` slots).
- `useNullIfEmpty: true` — submit `null` instead of an empty string when the
  field is left blank.
- `requiredRole` — only users with this role see / can use the field
  (server-side enforcement still required).
- `exclusiveGroup` / `exclusiveLabel` — group several mutually-exclusive
  fields under a single radio-style picker.
- `canCopy: true` — show a copy-to-clipboard button next to the value.
- `expandable` — allow long values to expand inline.
- `autoComplete: true` — turn on browser autocomplete for the input.
- `href` / `target` — render the value as a link (paired with
  `type: "link"`); both fields support templating (see Templating below).

## Dynamic property expressions

Most attributes above can be computed at runtime instead of hard-coded.
Place the expression as a **string** under a sibling `dynamic` object on the
property. Canopy re-evaluates each expression every time the form values
change and overwrites the matching attribute on the live property. Use this
to make a field conditionally hidden, conditionally read-only, or to pick
its `values` / `defaultValue` / `max` / `min` / `label` from another field's
current value.

Each expression is a **single JavaScript expression** (not a statement
block). It runs in a locked-down sandbox with these inputs:

- `item` — the current item being viewed/edited (undefined on Create).
- `data` — the live form values the user has entered so far.
- `params` — URL path parameters.
- `query` — URL query parameters.
- `auth` — the current session's auth context (api key, role, tenant, …).
- `path` — a helper for navigating the property's own path
  (`path.parent()`, `path.child("…")`, `path.prev()`, `path.next()`,
  `path.toString()`, `path.toParts()`); plus `get(obj, path, default)`.

Hard constraints (enforced; the expression is rejected if violated):

- No `;` — one expression only, no statements.
- No `return`, no arrow functions (`=>`), no `function(...)` /
  `Function(...)`, no `eval`. The result of the expression *is* the value.
- Globals (`window`, `global`, `document`, `fetch`, …) are shadowed to
  `undefined`; only the inputs above are reachable.
- Two attributes cannot be made dynamic: `dynamic` itself, and (for
  `nested` / `array` types) the inner `properties` / `items`.
- Inputs are deep-cloned and frozen — the expression cannot mutate them.
- If the expression throws, the static fallback (the literal value of the
  attribute on the property) is used and an error is logged to the console.

Shape — `dynamic` is a sibling of the static attributes. Each key under
`dynamic` overrides the same-named static attribute at runtime. Any of the
property attributes listed earlier can be made dynamic this way (visibility
flags, `readOnly`, `label`, `values`, `min`/`max`, `defaultValue`, …).

```jsonc
"<propertyKey>": {
  "label": "<static label>",
  "type": "text",
  "readOnly": false,                       // static fallback
  "dynamic": {
    "readOnly":   "<JS expression returning boolean>",
    "label":      "<JS expression returning string>",
    "excludeFromUpdate": "<JS expression returning boolean>"
  }
}
```

Concrete patterns:

- **Conditional visibility** — `dynamic.excludeFromCreate` /
  `excludeFromUpdate` / `excludeFromDetail` set to a boolean expression on
  `data` or `item`, e.g. `"item?.status === 'CLOSED'"`.
- **Conditional read-only** — `dynamic.readOnly` toggles based on role or
  another field, e.g. `"auth.role !== 'admin'"`.
- **Dependent enum options** — `dynamic.values` returns a different
  `[{ name, value }, …]` array depending on a sibling field.
- **Dependent numeric bounds** — `dynamic.max` / `dynamic.min` derived from
  another numeric field, e.g. `"data?.totalAmount ?? 0"`.
- **Computed label / placeholder** — `dynamic.label` keyed off
  `data?.<otherField>` so the prompt updates as the user types.

Use the static value as a sensible fallback so the form still renders if
the expression returns `undefined` or throws.

## Forms (no collection backing)

Use `forms[]` for standalone interactions (no underlying CRUD). The lifecycle
is **prepare → render → submit → response**.

```jsonc
{
  "id": "card-payment", "title": "Card Payment",
  "subpath": "card-payment",
  "properties": {
    "cardNumber": { "label": "Card", "type": "text" },
    "reservationBalance": { "label": "Balance", "type": "text", "readOnly": true }
  },
  "prepare": { "function": { "path": "myapp.payments.fetchBalance",
                             "type": "server",
                             "arguments": { "reservationId": { "queryParam": { "key": "reservationId", "type": "text" } } } } },
  "submit":  { "function": { "path": "myapp.payments.applyPayment",
                             "type": "server",
                             "arguments": { "body": { "data": true } } } },
  "response": { "type": "confirmation", "title": "Applied",
                "redirect": "/forms/card-payment?reservationId={{data.reservationId}}" }
}
```

`prepare` can return either a flat data object that pre-fills fields, or a
map of property overrides (`{ defaultValue, max, readOnly, values }`) for
runtime-driven UI changes (e.g. dynamic enum values, conditionally
read-only).

Form-level options:

- `type: "page"` (default) renders as a full page; `type: "modal"` opens
  the form in a dialog.
- `showSidebar`, `showHeader`, `showBreadcrumb` — chrome toggles when the
  form is rendered as a page; `showHeader: false` hides both header and
  breadcrumb.
- `cancel` — `false` hides the cancel button; `{ label, location:
  "top" | "bottom" }` overrides the label and position.
- `confirm` — `true` for a default confirmation dialog before submit, or
  `{ title, text, variant: "primary" | "secondary" | "destructive" }`.
- For standalone form submit buttons, `submitMode: "all" | "changed" |
  "filled"` controls which form values are included in the payload.
- The submit button itself accepts: `label`, `icon` (icon name, e.g.
  `"search"`, `"send"`), `variant: "primary" | "secondary" | "destructive"`,
  and `location: "top" | "bottom"` — position of the button on the page.

What matters most for customer authoring:

- The form submits the collected field values to the function you point it at.
- `arguments` decides whether the function receives the whole form payload,
  one field, the current item id, path params, or query params.
- `submitMode` matters when your backend expects either the full object or
  only the fields the user changed/filled in.
- `confirm` and `response` are optional UX wrappers around the same function
  call.

### Multi-submit forms

`submit` may be either a single object or an array, in which case each
entry becomes a separate button on the form:

```jsonc
"submit": [
  { "label": "Save Draft",
    "submitMode": "filled",
    "function": { "path": "myapp.orders.saveDraft", "type": "server" } },
  { "label": "Submit Order",
    "confirm": { "title": "Submit?", "text": "This sends the order.",
                 "variant": "primary" },
    "function": { "path": "myapp.orders.submit", "type": "server" },
    "response": { "type": "toast",
                  "toast": { "title": "Order submitted" },
                  "redirect": "/{{appId}}/collections/orders/{{data.id}}" } }
]
```

Use multi-submit only when one form genuinely supports different business
outcomes, for example **Save draft** vs **Submit**. In that case each button
points to its own function or response behavior. If there is only one real
outcome, keep a single submit button and focus on the payload mapping.

## Item pages

A collection's `itemPages` array attaches extra views and actions to each
item. Four kinds, distinguished by the keys present:

- **Sub-page** (`{ id, actionName, function, properties }`) — a custom
  read-only or interactive view rendered from the result of `function`,
  laid out by `properties`.
- **Sub-collection** (any sub-page that also has `list` / `get` etc.) —
  exactly the same shape as a top-level collection but nested under one
  parent item; arguments may use `pathParam` to receive the parent id.
- **Sub-route** (`{ id, actionName, subPage }`) — a link to another
  Canopy route (`subPage` is the route segment).
- **Submit page** (`{ id, actionName, submitFunction, responseForm,
  fields?, texts? }`) — a one-shot form (no underlying CRUD) attached to
  one item, useful for actions like "Send invoice".

Each item-page entry can also control where the action appears (`primary`,
`secondary`, `menu`) and whether it should surface directly on the card via
`visibleOnCard: true`.

## Actions and placement

In addition to the built-in CRUD buttons, `collections[].actions` and
`itemPages[].actions` let you attach extra operations that call a function,
optionally ask for confirmation, and optionally redirect afterwards:

```jsonc
"actions": [
  {
    "label": "Export CSV",
    "icon": "Download",
    "type": "default",
    "size": "sm",
    "placement": "secondary",
    "menuOrder": 10,
    "function": { "path": "myapp.orders.exportCsv", "type": "server" },
    "redirectTo": "/{{appId}}/collections/orders",
    "redirectWithQueryParams": true
  }
]
```

- `placement` lets you decide whether the action is shown prominently or kept
  in the overflow menu.
- `menuOrder` matters only when you have several menu actions and want them in
  a specific order.
- `confirmText` asks for confirmation before running.
- `responseForm` — `{ message?, properties? }` — shows result data after the
  function returns. Use `message` for a static outcome string, `properties`
  for a rendered property map populated from the function's return value.
  Both fields are optional; you can use either or both together.
- `redirectTo` (templatable) navigates after the action;
  `redirectWithQueryParams: true` carries the current query string along.

## MFA gating

For sensitive actions you can require an MFA token before the function
runs:

- On a CRUD action (`update`, `delete`) or any submit, set
  `mfaSupported: true`. Canopy then prompts the user for an MFA token
  before invoking the function.
- If your function expects the MFA token as an input, map it with
  `mfaToken: true` in the function arguments.
- Use `mfaRequiredActionsKey` only when this action should participate in the
  tenant's MFA policy configured in PolyUI.

The customer authoring the JSON only chooses *whether* to support MFA and
how the token is plumbed through. The rules of *when* MFA is enforced live
in the tenant's MFA config, not the application JSON.

## Common pattern: search -> results -> detail

Model it like this:

- Use a top-level `items` collection for the result list, for example
  `books`.
- Put the search inputs either directly in the collection as properties bound
  to `queryParam`, if the list should refresh from URL-driven filters, or in a
  standalone `forms[]` page if search is a separate step before the list.
- Point `list.function` at a function that returns the matching books.
- Use `list.propertyMapping` so each result row has an `id`, title/name, and
  optional description.
- Enable `itemActions: ["get"]` and point `get.function` at a function that
  returns the full details for one selected book.
- Define the detail `properties` with the richer fields you want to show once
  the user clicks into the item.

Minimal mental model:

- `queryParam` carries the search term or filters.
- `list` populates the result cards.
- `get` populates the selected item's detail view.

Example shape:

```jsonc
{
  "id": "books",
  "name": "Books",
  "properties": {
    "search": { "label": "Search", "type": "text", "queryParam": "q", "excludeFromDetail": true },
    "title": { "label": "Title", "type": "text" },
    "author": { "label": "Author", "type": "text" },
    "summary": { "label": "Summary", "type": "multiline" }
  },
  "itemActions": ["get"],
  "list": {
    "function": {
      "path": "library.books.search",
      "type": "server",
      "arguments": {
        "query": { "queryParam": { "key": "q", "type": "text" } }
      }
    },
    "propertyMapping": {
      "id": "id",
      "name": "title",
      "description": "author"
    }
  },
  "get": {
    "function": {
      "path": "library.books.getById",
      "type": "server",
      "arguments": {
        "id": { "id": true }
      }
    }
  }
}
```

If the user journey should start on a dedicated search screen, add a
standalone form first and redirect into the collection route with the query
string populated, for example `/{{appId}}/collections/books?q={{data.search}}`.

## Login, sign-up, and SSO

`login` and `signUp` configure the entry screens:

```jsonc
"login": {
  "title": "Login To My App",
  "logoSrc": "https://…logo.png",
  "allowPolyApiKey": true,
  "identityProviders": [
    { "id": "<idp-id>", "name": "Acme SSO", "iconUrl": "…",
      "providerSlug": "acme" }
  ],
  "recaptchaSiteKey": "…",
  "loginToPoly": false,
  "redirectTo": "/{{appId}}/collections/dashboard"
}
```

- `allowPolyApiKey: true` shows the "paste API key" panel alongside SSO
  buttons; set it to `false` for SSO-only apps.
- `identityProviders` references identity providers configured in PolyUI
  (Admin → Identity Providers); each entry needs the IdP's `id`.
- `recaptchaSiteKey` (and its server-side `recaptchaSecretKey`) gate the
  login form behind reCAPTCHA.
- `loginToPoly: true` makes the login flow target the Poly platform itself
  (used by PolyUI); customer apps usually leave it `false`.
- `redirectTo` is the post-login landing route; supports templating.
- `additionalInfo` is an array of strings or `[{ type: "text" | "link",
  value, url? }]` for legal text / sign-up links beneath the form.

`signUp.steps` is an ordered list of `PageConfig`s; each step owns its own
`fields`, `submit`, `texts`, and `additionalInfo`. The step-by-step shape
is covered in the public docs under *Metadata SignUp Attributes*.

## Choosing functions

From a Canopy authoring perspective, the important question is not how the
function is implemented internally, but what inputs it expects and what data
shape it returns.

- Point CRUD actions, standalone forms, and custom actions at Poly functions
  that already exist in the same tenant/environment.
- In customer-facing apps, the usual choice is a **server function** that
  accepts either the full form payload or a few mapped arguments.
- If the user is editing or creating records, make the function contract line
  up with the form payload you submit.
- If the screen is only reading data, make the function return the fields your
  collection or page needs to render.
- Do not point Canopy directly at a client-only function; expose a server-side
  entrypoint instead.

## Argument mapping

Argument mapping is where you decide what Canopy sends into the function.
This is the main integration surface a customer author needs to think about.

Common mappings:

- `data: true` — send the whole form or item payload.
- `data: "<propertyKey>"` — send one specific field.
- `id: true` — send the current item id.
- `pathParam` / `queryParam` — carry route state from the URL into the
  function. Each takes an object: `{ "key": "<paramName>", "type": "text" | "number" }`.
- `value` — send a fixed constant.
- `variableId` / `variablePath` — resolve a Poly variable server-side.
- `fallback` — provide a default value when the primary source is absent,
  e.g. `{ "queryParam": "page", "fallback": { "data": 1 } }` sends the
  `page` query param or `1` if it is missing.

Less common but supported mappings include `apiKey`, `tenant`,
`environment`, and `mfaToken`.

### Filter controls on list collections

When a `list.function` argument uses a `queryParam` object with extra fields,
Canopy renders a filter control above the collection list — the user's
selection updates the URL and re-fetches the list automatically.

Only `key` is required. Everything else is optional:
- `key` — URL query parameter name **(required)**.
- `type` — `"text"` renders a search input; `"enum"` renders a dropdown.
  Defaults to `"text"` if omitted.
- `label` — label shown above the control.
- `allowEmpty` — whether the dropdown shows a blank option.
- `defaultValue` — pre-selected value on first load.
- `values` — fixed `[{ name, value }, …]` options (for `type: "enum"`
  with a known set of choices).
- `functionValues` — `{ function, valueKey, nameKey }` for a dynamic enum
  whose options come from another function (use when the list of choices
  is not fixed).

Example — paginated list with a hotel dropdown filter and text search:

```jsonc
"list": {
  "paginated": true,
  "function": {
    "path": "myapp.records.list",
    "type": "server",
    "arguments": {
      "hotelId": {
        "queryParam": {
          "key": "hotelid",
          "type": "enum",
          "label": "Hotel",
          "functionValues": {
            "valueKey": "value",
            "nameKey": "label",
            "function": { "path": "myapp.hotels.list", "type": "server" }
          }
        }
      },
      "status": {
        "queryParam": {
          "key": "filter",
          "type": "enum",
          "label": "Status",
          "allowEmpty": false,
          "defaultValue": "ACTIVE",
          "values": [
            { "name": "Active", "value": "ACTIVE" },
            { "name": "Archived", "value": "ARCHIVED" }
          ]
        }
      },
      "search": {
        "queryParam": {
          "key": "search",
          "type": "text",
          "label": "Search",
          "allowEmpty": false,
          "defaultValue": ""
        }
      },
      "page": {
        "queryParam": "page",
        "fallback": { "data": 1 }
      }
    }
  }
}
```

Note: `"queryParam": "page"` (a plain string) is a shorthand for
`{ "key": "page", "type": "text" }` without the filter control UI — use the
shorthand when you just want to pass a query param through without rendering
a visible filter widget.

## Variables and Secrecy

Set per variable in PolyUI:

- **NONE** — value visible in PolyUI and to functions. Default.
- **OBSCURED** — masked in PolyUI; functions still read the plain value.
- **PARTIAL** — for object values, only object keys whose name contains
  `secret` are masked in PolyUI / treated as secret; sibling keys (e.g.
  `instanceUrl`, `appId`) stay readable. Example: a `myapp.credentials`
  variable with `{ "appId": "…", "secretKey": "…" }` — `appId` stays
  readable, `secretKey` is protected. Keys such as `password`, `token`, or
  `apiKey` should be renamed to include `secret` (or the whole variable
  should use `SECRET`) if they must be protected by the PARTIAL rule.
- **SECRET** — value fully encrypted; functions only get a reference,
  swapped in at the gateway.

Reference variables either via `variableId` / `variablePath` (server-side
resolution) or, in execute-function arguments, with the `PolyVariable::<Name>`
prefix (client-side substitution).

## Templating

Template variables depend on where the string is rendered; there is not one
global template context for every surface.

- Link-property `href` / `target` templates mainly receive
  `{{pathParams.x}}`, `{{searchParams.x}}`, and `{{value}}`, where `value`
  is the current property's value.
- Form `response.redirect` templates receive `{{auth.*}}`,
  `{{pathParams.x}}`, `{{searchParams.x}}`, `{{item.*}}`, and `{{data.*}}`.
- Sign-up `redirectTo` templates receive `{{appId}}`, `{{data.*}}`, and
  `{{result.*}}`; `redirectWithQueryParams: true` appends the current query
  string after templating.

Examples:

- `"href": "/{{pathParams.appId}}/collections/orders/{{value}}"`
- `"redirect": "/forms/card-payment?reservationId={{data.reservationId}}"`
- `"redirectTo": "https://upstream/{{result.code}}"`

## Response config

`response` shapes:

- `redirect` — `{ type: "redirect", redirect: "<url>" }`. Just navigate.
- `modal` — `{ type: "modal", modal: { title, message?, properties? },
  redirect? }`. Open a modal with the configured fields populated from the
  function's return value; the optional `redirect` runs after dismissal.
- `toast` — `{ type: "toast", toast: { title, description?, variant?:
  "default" | "destructive" }, redirect? }`. Lightweight notification.
- `inline` — `{ type: "inline", inline: { title?, properties? }, redirect? }`.
  Render the result below the original form without leaving the page.
  `properties` is a standard property map populated from the function's
  return value.
- `confirmation` — `{ type: "confirmation", confirmation: { title?, message?,
  properties? }, redirect? }`. Replace the form contents with a success /
  detail view. `message` is a static string shown above the properties;
  `properties` is a standard property map.

`redirect` strings are templatable (see Templating), so the post-submit
URL can pull values out of the form result (`{{data.id}}`) and, on form
responses, from the current query string (`{{searchParams.code}}`).

## Deploy via PolyUI

1. PolyUI → **Applications** → existing app → **Update**, or → **+ Create**.
2. Fill **Name**, **Description**, **Visibility** (`Environment` /
   `Tenant` / `Public`), and paste the full Application JSON into **Config**.
3. Submit. The deployed app is at `/canopy/<subpath>/login`. The API key
   shown in the header (e.g. *Alice — Production — Developer Key*)
   determines the tenant and environment the change lands in; referenced
   functions and variables must exist in that scope.

CI / integrators may automate the same submit via `PUT /applications/{id}/config`,
but the customer workflow is UI-only.

## Common mistakes

- Setting `function.type: "client"` — not a valid type. Wrap client
  functions in a server function instead.
- Omitting `propertyMapping` on a `list` so cards render blank.
- Referencing a function or variable that lives in a different tenant or
  environment than the API key submitting the Config.
- Marking everything `SECRET` when `PARTIAL` would leave non-secret fields
  readable in PolyUI.
- Trying to call deployment REST endpoints by hand instead of using PolyUI.
- Mixing `data: true` (whole payload) with `data: "<key>"` (single field) on
  the same argument.
- Using `readOnly` when the field should disappear from the form (use
  `excludeFromCreate` / `excludeFromUpdate` instead) — `readOnly` still
  submits the value.
- Using `Update` with `submitMode: "all"` over a partial schema — Update
  defaults to sending every property, which can overwrite fields the user
  never saw. Set `submitMode: "changed"` for partial-PATCH-style backends.
- Putting dynamic-expression strings directly on the static attribute
  (`"excludeFromCreate": "data?.x"`) instead of under `dynamic`. The
  static attribute must be a literal; dynamic overrides go under
  `property.dynamic.<attrName>`.
- Forgetting `mfaSupported: true` on an action whose function expects an
  `mfaToken: true` argument — the prompt will not appear and the function
  receives `undefined`.
- Defining a sub-collection under `itemPages` without a `pathParam`
  argument referencing the parent id, so the inner `list` returns the
  unscoped global list.
- Using `type: "json"` for free-form objects when `type: "nested"` (with
  declared sub-properties) would give better validation and a friendlier
  form.
