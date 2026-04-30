# Canopy Config, UI, and Runtime Reference

## Collection Config vs API Config

Every feature that lives under `/<appId>/collections/<collection>/...` is
backed by `polyapi_config/collections/<collection>/collection.json` and an
optional sibling `api.json`. The folder name equals the URL segment, e.g.
`/polyui/collections/server-functions/<id>/execute-server-function` is
backed by `polyapi_config/collections/server-functions/`. There are many
collection folders (api-functions, server-functions, client-functions,
webhooks, triggers, tables, schemas, applications, environments, users,
api-keys, variables, auth-providers, identity-providers, permission-policies,
access-logs, activities, jobs, snippets, saved-requests, tenant,
graphql-subscriptions, helpful-links, plus the `public-*` and
`autogen_apis` variants). Always identify the right one(s) for the URL or
feature you are changing instead of assuming a single canonical pair.

`collection.json` controls:

- properties, labels, field types, visibility, read-only state
- dynamic property expressions
- list filters through `queryParam`
- item pages and subcollections
- actions and action placement
- mapping runtime values into function arguments

`api.json` controls:

- PolyAPI function specs
- arguments, URL template, request body mode, return schema
- visibility and validation
- `removeIfNotPresentOnExecute`

Read both before debugging collection behavior.

## Optional Filters and Params

Implementation anchors:

- `src/components/collection/FilterField.tsx` deletes a query param when the new
  value is empty.
- `src/api/poly/function.ts` normalizes empty strings and empty arrays to
  `undefined`.
- `getExecutionBody` omits missing values only when
  `removeIfNotPresentOnExecute` is true.

Access Logs example:

- Status values are `success` and `failure`.
- "All" or empty state should mean no `status` param, not `status=`.
- The Canopy UI path typically invokes the Poly function gateway, so direct REST
  success does not prove gateway config correctness.

## Property Rendering

Implementation anchors:

- `src/components/collection/PropertyItem.tsx`
- `src/components/collection/PropertyField.tsx`
- `src/components/collection/utils.ts`
- Typed field components: `TextTypeField`, `MultilineTypeField`,
  `NumberTypeField`, `BooleanTypeField`, `CheckboxTypeField`,
  `LegalCheckboxTypeField`, `EnumTypeField`, `PickerTypeField`,
  `DateTypeField`, `DateTimeTypeField`, `TimeTypeField`, `JsonTypeField`,
  `CodeTypeField`, `ArrayTypeField`, `MultiTypeField`, `NestedTypeField`,
  `VariableTypeField`, `ExclusivePropertyField`.
- Form composition: `FormFields.tsx`, `FilterField.tsx`,
  `ListItemProperty.tsx`, `DetailsPage.tsx`, `Description.tsx`,
  `ResponseFormDialog.tsx`.
- List/grouping: `CollectionList.tsx`, `GroupedCollections.tsx`,
  `AppSidebar.tsx`.

Rules:

- Rendering is selected by configured `property.type`.
- Use `type: "json"` for arbitrary JSON payloads requiring JSON UI.
- `permissions` is currently fixed nested booleans in API key config.
- Future arbitrary API key `claims` should be `type: "json"` if backend/API
  contracts confirm claims exist.
- `readOnly: true` renders display-style UI in forms with a hidden input.
- `excludeFromSubmit` and `excludeFromUpdate` affect payload construction.

## Dynamic Properties

`src/lib/sandbox.ts` evaluates dynamic expressions with:

- `item`
- `data`
- `params`
- `query`
- `auth`
- `path`

Auth shape is `auth.user.role`, not `auth.user.roles`.

Dynamic property support does not automatically mean arbitrary dynamic action
fields are supported.

## Actions and Menus

Relevant files:

- `src/components/action-bar/ActionBar.tsx`
- `src/components/action-bar/ActionBarMenu.tsx`
- collection `actions` and item page `actions`

Rules:

- `ActionBar` separates destructive actions.
- Menu sorting uses `menuOrder ?? 999`.
- Use a large `menuOrder` to force a non-delete menu item near the bottom.
- Delete rendering in `ActionBarMenu` is sensitive; do not refactor it as a side
  effect.
- Confirm target context: collection list/detail, item detail, item page,
  subcollection list, or subitem detail.
- Keep route TSX generic; only add code when config cannot express behavior.

## React Component Boundaries

Extract a named child component when:

- the block has independent state, effects, derived data, or handlers
- only part of the page should re-render
- the parent becomes hard to reason about

Use memoization only for real cost, stable child props, or dependency
correctness. Do not add `React.memo`, `useMemo`, or `useCallback` everywhere by
default.

Good extraction candidates:

- execute-function argument controls
- variable selection/path suggestion UI
- saved-request action/status blocks
- specialized response rendering
- large action/menu branches

## Function Execution

Key files:

- `src/api/poly/function.ts` - canonical execution helpers
  (`executeApiFunction`, `executeServerFunction`, `executeRawFunction`,
  `getExecutionBody`).
- `src/api/poly/collection.ts` - list/get/create/update/delete orchestration
  for collections; access-log merge behavior.
- `src/api/poly/page.ts` - `submitPage` for item subpages, execute-function
  pages, and trigger-webhook pages. Routes through the same execution helpers.
- `src/api/poly/webhook.ts` - `triggerWebhookHandle` direct webhook calls
  (used by `trigger-webhook` route, may attach internal Poly API key).
- `src/components/custom/execute-function/*` - `ExecuteFunctionAction`,
  `ExecuteFunctionArguments`, `FunctionArgument`, `FunctionVariableArgument`
  and saved-request helpers.
- `src/app/[appId]/collections/[collectionId]/[itemId]/execute-api-function/*`
- `src/app/[appId]/collections/[collectionId]/[itemId]/execute-server-function/*`
- `src/app/[appId]/collections/[collectionId]/[itemId]/trigger-webhook/*`
- `src/app/[appId]/collections/[collectionId]/[itemId]/[pageId]/*` -
  `ItemPage`, `SubmitPage`, `SubmitPageFormContent`,
  `SubmitPageResponseContent`, `SubcollectionItems`, plus
  `[subItemId]/` for nested subitem detail.
- `src/app/[appId]/collections/[collectionId]/[itemId]/edit/*` and
  `.../create/*` - generic edit/create pages.
- `src/app/[appId]/collections/[collectionId]/[itemId]/@modal/delete/*` -
  parallel-route delete confirmation modal.
- `src/app/[appId]/forms/[formId]/*` - standalone form pages with their own
  layout and refresh button.

Function types:

- `api` and `server` route through Poly function gateway.
- `query` routes through table/query execution.
- `raw` calls a direct URL, builds its own headers, and has a host allowlist.

MFA token rule:

- `getExecutionBody(..., mfaToken)` only puts MFA in the body if config maps
  it.
- `executeRawFunction(..., method, mfaToken)` sets the `x-otp` header.
- Compare inline `collection.ts` raw branches with canonical `executeFunction`
  before copying them.

Execute-page current contract:

- `POLY_VARIABLE_NAME_PREFIX = "PolyVariable::"`.
- `getBody` emits `{ type: "PolyVariable", id }` for variable fields.
- Current branch does not contain a checked-in `PolyVariablePath::` prefix.

If adding nested variable path support:

- gate the path UI to object-like variable values
- preserve the user-entered path unless normalization is requested
- lazy-load selected variable details instead of N+1 loading all variables
- keep UI field names and parser behavior synchronized

