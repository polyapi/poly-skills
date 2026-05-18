# Canopy UI — Schema Reference

## Properties

Supported `type` values: `text`, `multiline`, `number`, `boolean`, `enum`,
`multi`, `nested`, `array`, `json`, `code`, `checkbox`, `link`, `picker`,
`legalCheckbox`, `date`, `time`, `datetime`, `variable`.

Number properties accept: `min`, `max`, `step`, `units`.

Multiline: `autoSize`, `minRows`, `maxRows`.

Date/time/datetime:
- `min` / `max` — ISO strings.
- `dateStyle` / `timeStyle`: `"full" | "long" | "medium" | "short"`.
- `hourCycle: "h12" | "h24"`.
- `inputTimeZone` / `outputTimeZone` — IANA names (e.g. `"America/Los_Angeles"`).

Enum-style (`enum`, picker variants):
- `values` — fixed `[{ name, value, readOnly? }, …]`.
- `functionValues` — `{ function, valueKey?, nameKey? }` (defaults `valueKey: "id"`, `nameKey: "name"`).
- `defaultValues` — array of `ArgumentMapping` entries.
- `queryParam` — bind to URL query param.
- `allowEmpty: true` — add blank option.
- `showValue: true` — display underlying `value` next to `name`.

Picker (`type: "picker"`):
- `pickerName` / `pickerLabel` — modal title / button label.
- `pickerValues: [{ name, function, valueKey?, nameKey? }, …]`.
- `itemType: "text" | "number"`.

Variable (`type: "variable"`):
- `variableType` — scalar type (any except `array`, `nested`, `multi`, `variable`).
- `asReference: true` — store as `{ type: "PolyVariable", id }` reference.

Legal-checkbox (`type: "legalCheckbox"`):
- `orgName`, `url`, `requiredError`.

Nested/array:
- `type: "nested"` — sub-fields group with its own `properties`. Optional `expandable: true | "<label>"`.
- `type: "array"` — repeatable group. `items: { type: "nested", properties: { … } }`. Optional: `canAddItems`, `canRemoveItems`, `pagination`, `itemLabelProperty`.
- `type: "multi"` — accepts several `FieldType`s (`string | number | boolean | object`).

Code/JSON:
- `type: "code"` requires `language` (e.g. `"javascript"`, `"sql"`). Accepts `hideLanguage: true`.
- `type: "json"` accepts `hideLanguage: true`.

Layout/link hints (any type):
- `flex: true` — share a row with siblings.
- `inset: true` — indent as part of a logical group.
- `href` / `target` — render as link (with `type: "link"`); both support templating.

---

## Strictly validated field reference

> Two nested objects — `CollectionProperty` and `ArgumentMapping` — are validated server-side
> with `forbidNonWhitelisted: true`. Any unknown key causes a **"property X should not exist"** error.

### `ArgumentMapping` — allowed keys

| Key | Type | Meaning |
|---|---|---|
| `value` | `any` | Hard-coded constant |
| `data` | `true` or `"fieldKey"` | `true` = whole payload; `"fieldKey"` = one field |
| `id` | `true` (boolean only) | Current item's ID — must be literal `true` |
| `queryParam` | `string` or property object | URL query parameter |
| `pathParam` | `string` | URL path parameter name |
| `fallback` | `ArgumentMapping` | Value when primary source is absent |
| `variableId` | `string` | Poly variable UUID (server-side) |
| `variablePath` | `string` | Poly variable dotted path (server-side) |
| `apiKey` | `boolean` | Inject current API key |
| `tenant` | `boolean` | Inject current tenant ID |
| `environment` | `boolean` | Inject current environment ID |
| `mfaToken` | `boolean` | Inject MFA token (only when `mfaSupported: true`) |

**Nothing else is valid.** Common wrong keys: `fixed` (use `value`), `data: "fieldName"` inside payload sub-objects.

> **Critical constraint — `ArgumentMapping` is validated server-side.**
> Every value inside a function's `arguments` object is validated as an
> `ArgumentMapping`. This means you cannot place arbitrary sub-objects there;
> each value must use one of the recognised mapping keys above. In particular:
>
> - `id: true` (boolean) tells Canopy to inject the current item's ID.
>   It is **not** a reference to a form field named `id`.
> - `id: { "data": "someField" }` is **invalid** — the validator rejects a
>   non-boolean value for `id`. If you want to send a form field, map it
>   through the argument name that your function actually expects, e.g.
>   `"recordId": { "data": "id" }`.
> - Unknown keys inside an `ArgumentMapping` also fail validation (the
>   server uses `forbidNonWhitelisted: true`). Never invent keys that are
>   not in the recognised set.

> **Facade / router functions — send the whole payload, not individual fields.**
> When a backend function accepts a generic `payload` argument and dispatches
> internally (a facade or router pattern), map it as `"payload": { "data": true }`
> so Canopy sends the entire current form/item as that argument. Do not expand
> individual fields inside that argument's object (`"payload": { "fullName":
> { "data": "fullName" }, … }`) — those keys are not valid `ArgumentMapping`
> properties and the whole request will be rejected.

> Before handing off a facade/router-backed collection, verify the whole
> function contract exactly:
>
> - Copy the real top-level argument names, nesting, and request shape from the
>   checked-in function contract. Never infer this from naming alone.
> - If the function expects identifiers outside a generic payload object,
>   map those identifier arguments explicitly and do not assume `"payload": {
>   "data": true }` is sufficient by itself.
> - If the function accepts a generic payload object, use `"payload": {
>   "data": true }` only when the checked-in contract really accepts that
>   whole-object shape.
> - Verify the response shape too. Do not point Canopy list/get/detail config
>   at a facade/router that returns an extra wrapper object unless the runtime
>   path you are using explicitly unwraps it before rendering.

### `CollectionProperty` — allowed keys

**Identity / type**

| Key | Type |
|---|---|
| `key` | `string` |
| `type` | `"text"` \| `"number"` \| `"multiline"` \| `"boolean"` \| `"enum"` \| `"json"` \| `"multi"` \| `"nested"` \| `"array"` \| `"code"` \| `"picker"` \| `"datetime"` \| `"date"` \| `"time"` \| `"variable"` \| `"link"` |
| `label` | `string` |

Property definitions describe the field's type, label, validation, and UI behavior; they do not create the
runtime value by themselves. On collection pages, a field's value comes from the current item returned by the
list function or, for detail/edit, the get function. On Create and standalone forms, the initial value comes
from `defaultValue` and may be overridden by the prepare function.

Additional property attributes not captured in the table below:
- `requiredError` — custom message shown when a `required: true` field is left empty.
- `key: true` — use this property as the lookup key for CRUD instead of the default `id`.
- `hideOnCreate: true` — hide the field in the **Create** form only; field still appears in Update and detail (similar to `excludeFromCreate` but may still submit the value).
- `description` — alias for `helperText`; helper text rendered under the input.

**Validation / value**

| Key | Type |
|---|---|
| `required` | `boolean` |
| `defaultValue` | `any` |
| `values` | `Array<{ name, value, readOnly? }>` |
| `functionValues` | `{ function, valueKey?, nameKey? }` |
| `defaultValues` | `ArgumentMapping[]` |
| `min` | `number \| string` |
| `max` | `number \| string` |
| `step` | `number` |

**Visibility / form membership**

| Key | Type |
|---|---|
| `readOnly` | `boolean` |
| `excludeFromCreate` | `boolean` |
| `excludeFromUpdate` | `boolean` |
| `excludeFromDetail` | `boolean` |
| `excludeFromSubmit` | `boolean` |
| `hidden` | `boolean` |
| `hideIfEmpty` | `boolean` |
| `hideLabel` | `boolean` |
| `visibleOnCard` | `boolean` |
| `useNullIfEmpty` | `boolean` |
| `requiredRole` | `"USER"` \| `"ADMIN"` \| `"SUPER_ADMIN"` |
| `exclusiveGroup` | `string` |
| `exclusiveLabel` | `string` |
| `dynamic` | `Record<string, string>` — runtime JS expressions keyed by attribute name |

**UI / display**

| Key | Type |
|---|---|
| `placeholder` | `string` |
| `helperText` | `string` |
| `tooltip` | `{ title, value, url?, action? }` |
| `autoComplete` | `boolean` |
| `canCopy` | `boolean` |
| `inset` | `boolean` |
| `expandable` | `boolean` |
| `href` | `string` |
| `target` | `"_self"` \| `"_blank"` \| `"_parent"` \| `"_top"` |

**Text / multiline**

| Key | Type |
|---|---|
| `autoSize` | `boolean` |
| `minRows` | `integer` |
| `maxRows` | `integer` |

**Date / time**

| Key | Type |
|---|---|
| `dateStyle` | `"full"` \| `"long"` \| `"medium"` \| `"short"` |
| `timeStyle` | same |
| `hourCycle` | `"h12"` \| `"h24"` |
| `inputTimeZone` | IANA timezone string |
| `outputTimeZone` | IANA timezone string |

**Code / language**

| Key | Type |
|---|---|
| `language` | `string` |
| `hideLanguage` | `boolean` |

**Enum / picker**

| Key | Type |
|---|---|
| `queryParam` | `string` |
| `itemType` | `"text"` \| `"number"` |
| `itemLabel` | `string` |
| `itemLabelProperty` | `string` |
| `pickerName` | `string` |
| `pickerLabel` | `string` |
| `pickerValues` | `Array<{ name, function, valueKey?, nameKey? }>` |

**Nested / array**

| Key | Type |
|---|---|
| `properties` | `CollectionProperties` |
| `items` | `CollectionProperty` (without `key`/`label`) |
| `canAddItems` | `boolean` |
| `canRemoveItems` | `boolean` |
| `showIndex` | `boolean` |

**Multi-type**

| Key | Type |
|---|---|
| `types` | `Array<"string" \| "number" \| "boolean" \| "object">` |

**Variable**

| Key | Type |
|---|---|
| `variableType` | any scalar type |
| `asReference` | `boolean` |

**Not valid — will be rejected:** `pattern`, `regex`, `validate`, `format`, `mask`, `customValidator`,
`fixed`, `onChange`, `computed`, or any other key not in the list above.

### `FunctionType` — allowed keys

| Key | Required | Type |
|---|---|---|
| `type` | **yes** | `"server"` \| `"api"` \| `"query"` \| `"raw"` |
| `path` | one of `path`/`id` | dotted context path |
| `id` | one of `path`/`id` | function UUID |
| `operation` | no | `string` |
| `method` | no | `"GET"` \| `"POST"` \| `"PUT"` \| `"PATCH"` \| `"DELETE"` |
| `arguments` | no | `Record<string, ArgumentMapping>` |

Exactly one of `path` or `id` must be present. `type: "client"` is **not valid**.

---

## Collections — full field reference

Required: `id`, `name`, `properties`, `list`, `get`.

Collection `type` flavours:
- **`items`** (default) — standard list of records.
- **`item`** (singleton) — one record, no list view. Provide `get` and optionally `update`.
- **`custom-page`** — static page rendered from `elements[]` (`{ elementType: "text" | "field" }`) with optional `dataFunction` to pre-load values. Use for dashboards or info pages that aren't a list.

Extra attributes (default `items` type):
- `idProperty` — which property holds the row id; defaults to `"id"`.
- `nameProperty` / `descriptionProperty` — card title and subtitle fields.
- `description` — short blurb shown above the list.
- `propertyMode: "manual" | "auto"` — `auto` infers extra columns from list response.
- `inferredProperties` — hints for auto-inferred properties.
- `hiddenProperties` — array of property keys to hide everywhere.
- `actions` — extra collection-level buttons.
- `itemPages` — sub-pages, sub-collections, item-specific actions.

CRUD action options:
- `actionLabel` / `submitLabel` / `cancelLabel` — button text overrides.
- `create.submitMode: "all" | "filled"`.
- `update.submitMode: "all" | "changed" | "filled"` — `"changed"` is most common.
- `placement: "primary" | "secondary" | "menu"` and `menuOrder`.
- `delete.confirmTitle` / `confirmText`.
- `create.responseForm` — see Response config. For collections whose canonical key is not literally `id`,
  verify the full post-create flow before using `create.responseForm`. Some runtime paths use a synthesized
  `item.id` when closing the response dialog — either ensure the returned item exposes that alias, or avoid
  `create.responseForm` for that collection.
- `mfaSupported: true` and `mfaRequiredActionsKey` — per-action MFA gating.

`list.propertyMapping` maps row fields to `id` / `name` / `description` slots. Verify them against the
application path you are targeting — do not assume `propertyMapping` is always the only mechanism that
drives item identity or titles; it must stay consistent with `idProperty`, `nameProperty`, and any property
key remapping used by the same config. Extra keys such as `hours`, `status2`, or `customer` are not supported
by the declared mapping type and may be rejected by schema validation. Use `visibleOnCard: true` on properties
instead for additional card facts.
Add `paginated: true` plus `page` and `pageSize` `queryParam` arguments for paginated APIs.

---

## Filter controls on list collections

When a `list.function` argument uses a `queryParam` object with extra fields,
Canopy renders a filter control above the collection list.

- `key` — URL query parameter name **(required)**.
- `type` — `"text"` or `"enum"`. Defaults to `"text"`.
- `label` — label above the control.
- `allowEmpty` — whether the dropdown shows a blank option.
- `defaultValue` — pre-selected value on first load.
- `values` — fixed options for `type: "enum"`.
- `functionValues` — `{ function, valueKey, nameKey }` for dynamic enum.

Note: `"queryParam": "page"` (plain string) is shorthand for
`{ "key": "page", "type": "text" }` without rendering a filter widget.

---

## Item pages

Four kinds under `itemPages`:

- **Sub-page** (`{ id, actionName, function, properties }`) — custom view from `function`.
- **Sub-collection** — same shape as a top-level collection, nested under one parent; use `pathParam` for parent id.
- **Sub-route** (`{ id, actionName, subPage }`) — link to another Canopy route.
- **Submit page** (`{ id, actionName, submitFunction, responseForm, fields?, texts? }`) — one-shot form on an item.

Each entry can set `placement` (`primary`, `secondary`, `menu`) and `visibleOnCard: true`.

---

## Actions

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

- `confirmText` — ask for confirmation before running.
- `responseForm: { message?, properties? }` — show result data after the function returns.
- `redirectTo` (templatable) — navigate after the action.

---

## MFA gating

- Set `mfaSupported: true` on a CRUD action or submit to prompt for an MFA token.
- Map the token with `mfaToken: true` in function arguments if the function expects it.
- Use `mfaRequiredActionsKey` when the action should participate in the tenant's MFA policy.

---

## Dynamic property expressions

Place expressions as strings under a sibling `dynamic` object on the property.
Canopy re-evaluates each expression every time form values change.

Sandbox inputs: `item`, `data`, `params`, `query`, `auth`, `path`.

- `item` — current item being viewed/edited (undefined on Create).
- `data` — live form values.
- `params` — URL path parameters.
- `query` — URL query parameters.
- `auth` — current session auth context (api key, role, tenant, ...).
- `path` — helper for navigating the property path (`path.parent()`, `path.child("...")`,
  `path.prev()`, `path.next()`, `path.toString()`, `path.toParts()`), plus
  `get(obj, path, default)`.

Hard constraints:
- No `;` — one expression only.
- No `return`, no arrow functions, no `function(...)`, no `eval`.
- Globals (`window`, `document`, `fetch`, …) are shadowed to `undefined`.
- Cannot make `dynamic` itself or inner `properties`/`items` dynamic.
- Inputs are deep-cloned and frozen.
- If an expression throws, static literal fallback is used and an error is logged to the console.

```jsonc
"<propertyKey>": {
  "label": "<static label>",
  "type": "text",
  "readOnly": false,
  "dynamic": {
    "readOnly": "auth.role !== 'admin'",
    "excludeFromCreate": "item?.status === 'CLOSED'"
  }
}
```

---

## Forms (standalone)

Lifecycle: **prepare → render → submit → response**.

Form-level options:
- `type: "page"` (default) or `type: "modal"`.
- `showSidebar`, `showHeader`, `showBreadcrumb` — chrome toggles.
- `cancel` — `false` hides cancel; `{ label, location }` overrides.
- `confirm` — `true` or `{ title, text, variant: "primary" | "secondary" | "destructive" }`.
- `submitMode: "all" | "changed" | "filled"`.
- Submit button: `label`, `icon`, `variant`, `location: "top" | "bottom"`.

What matters most for customer authoring:
- The form submits the collected field values to the function you point it at.
- `arguments` decides whether the function receives the whole form payload, one field, the current item id, path params, or query params.
- `submitMode` matters when your backend expects either the full object or only the fields the user changed/filled in.
- `confirm` and `response` are optional UX wrappers around the same function call.

Multi-submit: `submit` can be an array; each entry becomes a separate button with its own function and response.

`prepare` returns partial `CollectionProperties` map — property overrides keyed by field name.

---

## Login, sign-up, and SSO

```jsonc
"login": {
  "title": "Login To My App",
  "logoSrc": "https://…logo.png",
  "allowPolyApiKey": true,
  "identityProviders": [{ "id": "<idp-id>", "name": "Acme SSO", "iconUrl": "…", "providerSlug": "acme" }],
  "recaptchaSiteKey": "…",
  "loginToPoly": false,
  "redirectTo": "/{{appId}}/collections/dashboard"
}
```

- `allowPolyApiKey: true` — shows API key panel alongside SSO. Set `false` for SSO-only.
- `loginToPoly: true` — targets Poly platform itself (PolyUI only); customer apps leave it `false`.
- `additionalInfo` — array of strings or `[{ type: "text" | "link", value, url? }]`.

`signUp.steps` — ordered list of `PageConfig`s; each step has its own `fields`, `submit`, `texts`, `additionalInfo`.

---

## Variables and Secrecy

- **NONE** — value visible everywhere. Default.
- **OBSCURED** — masked in PolyUI; functions read plain value.
- **PARTIAL** — only object keys whose name contains `secret` are masked.
- **SECRET** — fully encrypted; functions only get a reference.

Reference via `variableId` / `variablePath` (server-side) or `PolyVariable::<Name>` prefix (client-side).

---

## Templating

Context depends on surface:

- `href` / `target` — `{{pathParams.x}}`, `{{searchParams.x}}`, `{{value}}`.
- `response.redirect` — `{{auth.*}}`, `{{pathParams.x}}`, `{{searchParams.x}}`, `{{item.*}}`, `{{data.*}}`.
- Sign-up `redirectTo` — `{{appId}}`, `{{data.*}}`, `{{result.*}}`; `redirectWithQueryParams: true` appends query string.

Examples:
- `"href": "/{{pathParams.appId}}/collections/orders/{{value}}"`
- `"redirect": "/forms/card-payment?reservationId={{data.reservationId}}"`

---

## Response config

- `redirect` — `{ type: "redirect", redirect: "<url>" }`.
- `modal` — `{ type: "modal", modal: { title, message?, properties? }, redirect? }`.
- `toast` — `{ type: "toast", toast: { title, description?, variant?: "default" | "destructive" }, redirect? }`.
- `inline` — `{ type: "inline", inline: { title?, properties? }, redirect? }`.
- `confirmation` — `{ type: "confirmation", confirmation: { title?, message?, properties? }, redirect? }`.

`redirect` strings are templatable.
