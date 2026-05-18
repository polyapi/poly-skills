# Canopy UI — Generation Rules & Anti-patterns

## CRUD-from-tables: source-of-truth selection

Use these rules when generating a fresh CRUD app for tables in the current project.

- If the prompt asks for CRUD over **all tables** and table artefacts are present, treat the
  table artefacts as the primary source of collections, fields, primary keys, collection ids, and query paths.
- Prefer direct table query functions when table artefacts provide enough CRUD metadata and no
  checked-in Canopy app is to be reused.
- Do not point list/get at a facade whose response is wrapped in an envelope unless the wrapper is
  known to be unwrapped before Canopy receives it.
- If a table artefact has `context: <context>` and `name: <tableName>`, the table query path is `<context>.<tableName>`.
- When both table artefacts and source code exist, use source code only to refine UX labels,
  helper text, resource aliases, grouping, and validation hints. Do not let client-function CRUD
  wrappers override table-query CRUD unless a server-compatible facade is explicitly required.
- Validation or enum logic found only inside an unused wrapper function is supporting evidence,
  not the function contract. Reflect it only when it improves a simple table CRUD UI.

---

## Collection ids, primary keys, and display fields

- Set `idProperty` to the table column marked `primary: true`. Do not assume the primary key is named `id`.
- `list.propertyMapping.id` must point to the same primary-key field used by `idProperty`.
- Treat contract verification as a release gate: if route ids, lookup keys, argument names,
  payload shape, property keys, or response shape do not match the backend contract exactly,
  the config is wrong and must not be handed off.
- Use property keys exactly as returned by the table/function. Do not alias backend fields (e.g. do not alias `<primaryKey>` to `id` in `properties`).
- Default `collection.id` to the stable table artefact name. Use a shorter domain resource id only
  when the project artefacts clearly expose a one-to-one resource alias and the alias is the UI source of truth.
- If a source-code resource union/router mapping exposes `<resourceName>` for `<tableName>`, treat it
  as a naming hint, not an automatic override. Keep the table name for `collection.id` unless the prompt favours the domain alias.
- Avoid technical suffixes in user-facing collection names when a documented domain label exists.
- Choose `nameProperty` from the best human-readable column — name/title/description/project-like field.
  Avoid using technical ids as titles.
- `list.propertyMapping` must contain only `id`, `name`, and `description`. Use `visibleOnCard: true` for additional card facts.
- For `list.propertyMapping.description`, prefer a real descriptive/status/contact/notes field over a foreign-key field.
- Do not add collection-level `descriptionProperty` just because `list.propertyMapping.description` exists.

---

## Property generation from table columns

- Generate `properties` directly from table columns using the same keys and required flags.
- Map obvious numeric table columns to `type: "number"`; otherwise prefer `type: "text"` unless
  the table schema or active backend contract proves a richer Canopy type is required.
- For string columns, do not upgrade to `multiline`, `date`, or `enum` solely from a column name
  or from validation inside a non-called wrapper.
- Do not invent validation-only keys such as `pattern`, `format`, or custom validators.
- If source code validates a non-obvious user-entered format with a regex or explicit error message,
  reflect it as concise `helperText`. Prefer short noun-phrase helper text over instructional prose.
- Avoid adding helper text for obvious date/time/string fields unless the table artefact or UI spec
  explicitly documents a required format for the direct CRUD path.
- For primary keys that should not be changed after creation, set `excludeFromUpdate: true`.
- For direct table CRUD, do **not** set `excludeFromCreate: true` solely because source wrapper code
  generates an id; that wrapper is not called.
- If a primary key is proven server-assigned for the actual called create function, exclude it from Create.
  If direct insert expects/allows the user to provide it and the table marks it required, keep it visible.
- Mark a central numeric measure property as `visibleOnCard: true` when important to scan list items.
  Do not mark every numeric or status-like field visible by default.
- Avoid adding UI embellishments (`autoSize`, `minRows`, enum values, min/max/step, readOnly) unless
  directly supported by table schema, type definitions, or validation code.

---

## Item actions and CRUD buttons

- `create` is configured by the collection-level `create` object; it usually does not appear in `itemActions`.
- For simple CRUD table apps, `["get", "update"]` in `itemActions` is often enough.
- Configure `delete` when CRUD is requested, but do not add it to `itemActions` unless the UI should expose delete on each card.
- Use `Add <singularResourceLabel>` for `create.actionLabel` only when the label is clearly countable.
  For plural/mass concepts, use `Add <collectionLabel>`.
- Add `delete.confirmTitle` and `delete.confirmText` for destructive CRUD actions.
  Prefer `"This cannot be undone."` unless project copy says otherwise.
- Delete titles: `Delete <resourceLabel>?`. Avoid adding "record" unless the label requires it.

---

## List defaults

- Set `list.paginated: true` and pass a conservative `limit` via `{ "value": 1000 }` for unfiltered table lists.
- If source code shows an ordering preference, use it. Otherwise: stable readable field ascending for
  master-data tables, or a date/time field descending for activity/log/tracking tables.
- If no good subtitle exists, still provide `list.propertyMapping.description` and point it at the
  least-bad stable display field. Do not invent a fake property.
- If properties are fully declared manually and `propertyMode` is not `auto`, include `inferredProperties: {}`
  to make the no-inference intent explicit.
- If `propertyMode` or `propertyMapping` is ambiguous, do not guess from generic examples. Follow the
  targeted backend contract and keep the rest of the collection contract internally consistent.

---

## Collection names, descriptions, and grouping

- Use table descriptions and type names to create short user-facing `collection.description` strings.
  Prefer concise purpose statements over copying long implementation text.
- Remove redundant implementation words such as "records" when the collection name already implies stored rows.
- Avoid repeating the app/domain name in every collection description.
- Prefer specific collection names from table descriptions when they reveal the real subject. For example,
  if a technical table name stores a clearly named entity type, use the entity phrase as the collection
  `name` while keeping `collection.id` stable.
- Group collections by domain role when artefacts provide evidence: central people/entity/reference tables
  can use a specific domain group derived from the artefacts; dated records, logs, trackers, measurements,
  and operational records can share an activity/tracking-style group.
- Do not put a collection under generic `Master Data` when table descriptions expose a more specific category.
- Do not put every collection under the broad app/domain name if more specific groupings are evident from
  table descriptions, resource names, or relationships.
- Do not invent highly specific group names from one fixture. Use generic, evidence-based group labels that
  match the domain vocabulary visible in the project artefacts.

---

## Top-level output hygiene

- Output only fields needed by the Application JSON. Do not add `forms: []` when there are no standalone forms.
- If setting a generated `icon`, also set `login.logoSrc` to the same value for consistent branding unless a real logo source is provided.
- Prefer a deterministic generated avatar/logo URL based on concise initials from `<appName>` or the dominant domain phrase when no real logo asset exists. Avoid random stock-image URLs and avoid unnecessary styling query parameters unless required by the project.
- When deriving initials, use at most two or three significant words; ignore generic operational prefixes when a more distinctive domain phrase is evident.
- Keep `allowAppSwitcher: false` and `allowEnvironmentSwitcher: false` for focused customer CRUD apps.
- Derive `name` and `subpath` from the app/domain requested by the user and available project artefacts, not from old generated app files when the prompt says to ignore them.
- If artefacts reveal one central entity plus dependent/child tables, it is acceptable for the top-level app name and subpath to include the central entity label when that better describes the generated CRUD app. Do not append generic words such as `CRUD` unless requested.
- Set `login.allowPolyApiKey: true` for developer/operator CRUD apps unless the prompt specifies SSO-only.
  Set `login.title` to `<appName> Login` using the chosen app name without extra implementation qualifiers.

---

## Avoid these anti-patterns

- Do not use a server facade merely because it exists when the prompt asks for table CRUD.
- Do not send facade-style arguments (`resource`, `operation`, `payload`) to table query functions.
- Do not send table-query arguments (`where`, `data`, `limit`, `orderBy`) to a facade unless the facade explicitly declares those as its parameters.
- Do not use template strings such as `"{{id}}"` inside `value` objects for current item ids. Use `{ "id": true }`.
- Do not add descriptive or layout fields that are not supported by evidence.
- Do not use random external image URLs for `icon`/`logoSrc`.
- Do not choose `list.propertyMapping.description` from a foreign key when a direct description/status/note/contact field exists.
- Do not add `descriptionProperty`, helper text, enum values, `visibleOnCard`, or richer property types
  merely because they are valid Canopy fields.

---

## Common mistakes

- Setting `function.type: "client"` — not valid. More broadly: **never point Canopy directly at a client function even if you know its context path.** Client functions (`PolyClientFunction`) run in the browser and are not reachable from Canopy's server-side function dispatch. Always go through a server function (`PolyServerFunction`). If the repo uses a facade/router server function as the single Canopy entry point, all CRUD actions must call that server function — do not bypass it by pointing individual actions at the underlying client function.
- Assuming `propertyMapping` is the only thing that makes cards render — it must stay consistent
  with `idProperty`, `nameProperty`, and property key remapping.
- Adding extra keys to `list.propertyMapping` beyond `id`, `name`, `description` — not supported.
- Referencing a function or variable in a different tenant or environment than the submitting API key.
- Marking everything `SECRET` when `PARTIAL` would leave non-secret fields readable in PolyUI.
- Trying to call deployment REST endpoints by hand instead of using PolyUI for customer authoring flows.
- Mixing `data: true` (whole payload) with `data: "<key>"` (single field) on the same argument mapping.
- Using `readOnly` when the field should disappear (use `excludeFromCreate`/`excludeFromUpdate` instead).
- Using `Update` with `submitMode: "all"` over a partial schema — use `submitMode: "changed"`.
- Putting dynamic-expression strings directly on the static attribute (`"excludeFromCreate": "data?.x"`)
  instead of under `dynamic`. Dynamic overrides go under `property.dynamic.<attrName>`.
- Forgetting `mfaSupported: true` on an action whose function expects `mfaToken: true`.
- Defining a sub-collection under `itemPages` without a `pathParam` argument referencing the parent id.
- Using `type: "json"` when `type: "nested"` with declared sub-properties would give better validation.
- Adding a `pattern` field to a property definition — rejected by `forbidNonWhitelisted`.
  Use `helperText` to guide the user; enforce server-side.
- Using `fixed` as an `ArgumentMapping` key — not recognised. Use `value`.
- Setting `collection.id` to a non-string value (`true`, a number) — must be a string slug.
- Making property keys in `properties` differ from the field names the backend actually returns.
- Setting `list.propertyMapping.id` to hardcoded `"id"` when the backend's identifier field has a different name.
- Pointing `list.function` at a facade whose response envelope does not match what Canopy expects.
  Canopy list requires a flat array or `{ results: […], pagination: { count, page, pages, pageSize } }`.
- Pointing Canopy at a function with a single object parameter and then writing flat arguments for the object's inner fields.
- Using `"payload": { "data": true }` on a `get` operation — Canopy rejects it with "Missing Input"
  because there is no form data yet when `get` runs. Use `id: true` or fixed `value` arguments only for `get`.

<!-- REQUESTY_SKILL_OPTIMIZER_APPENDIX_END -->
