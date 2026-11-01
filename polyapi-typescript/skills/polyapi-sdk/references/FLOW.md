# TypeScript Flow Operations

## Discover the Installed Interface

Read project instructions and scripts, then check these help commands from the
workspace root. They describe the current TypeScript Flow template, not every
PolyAPI repository:

```bash
pnpm flow delete-content --help
pnpm flow logs --help
```

Keep the selected `ENVPATH` and resolved target consistent. Current Flow reuses
the workflow SDK's saved Poly setup, resolving that package through pnpm links;
environment overrides can select another connection. Let Flow load credentials
and OTP rather than printing keys, sourcing secret files or building new curl
wrappers. Preserve project branch and production safeguards. If a command is
missing, discover the repo's supported path instead of inventing flags or
installing tooling without a task need.

## Preview and Delete Resources

Use the configured namespace in place of `demo`. Start with a metadata preview:

```bash
pnpm flow delete-content --types api-functions,schemas --context demo.crm
```

This selects exactly `demo.crm`, preserving `demo.crm.contacts` and other
descendants. `--include-children` explicitly includes dot-separated descendants;
it is independent of recursive spec-folder discovery during training.
Deletion previews query the selected server, unlike offline training dry runs.

Only when existing user authorization covers this exact target, types and scope:

```bash
pnpm flow delete-content --types api-functions,schemas --context demo.crm --apply
```

Review the preview and satisfy the CLI's exact `DELETE` confirmation. Add
`--include-children` only if descendants are intended. Advice, log retrieval
or training alone grants no deletion authorization; reuse authorization already
given for cleanup rather than asking again for the same scope.

| Behavior | Operational meaning |
| --- | --- |
| No `--apply` | Preview only, even through the `delete:content` alias |
| `--types` | Multiple comma-separated resource kinds; `--type` is a TS alias |
| Exact context by default | Descendants require `--include-children` |
| Namespace ownership | Accessible shared resources are not automatically owned |
| 404 readback | Each DELETE is checked; HTTP success alone is insufficient |

Canonical kinds are `api-functions`, `client-functions`, `server-functions`,
`ai-functions`, `schemas`, `variables`, `webhooks`, `triggers`, `jobs`, `tables`
and `subscriptions`; verify availability with local help. Jobs and triggers
qualify only when every referenced server function is known and in scope.
Flow orders selected dependents before functions and schemas. Context selection
does not infer a dependency cascade across other contexts: inventory related
resources and include only the cleanup the user authorized. Preview metadata
without fetching variable values.

Deletion changes remote state, not checked-in artefacts. Flag local definitions
that a future push or training run could recreate; edit those files only when
permanent local removal is also within the user's requested scope.

If deletion or verification fails, stop; remaining resources may still exist.
Review the current plan before any authorized retry. When SDK absence matters,
regenerate from the same target using the project's supported SDK path and
check that deleted exports are gone. Separate confirmed removal from local
SDK state in the report.

## Read Server-Function Logs

Use the actual server-function ID, resolved from an authorized metadata listing
or the repo's existing registry. A name or SDK path is not an ID.

```bash
pnpm flow logs SERVER_FUNCTION_ID --logs-page 1 --logs-page-size 500 --limit 500 --keyword trace-123
```

This reads one page without invoking or deploying the function. `--keyword` is
a text filter, not a dedicated structured trace-ID selector. Use pagination
metadata to request further pages when needed; an empty filtered page does not
prove no invocation occurred. Limit defaults to page size. `--raw` returns the
original response when formatting hides needed diagnostic information.

Client-function logs appear within the calling server-function execution.
Reading logs does not require a write OTP; project connection requirements still
apply. Logs can contain credentials or customer payloads: retrieve a bounded,
relevant page and redact sensitive content before reporting or saving it.
Report function, target, page/filter, timestamps and relevant events, without
claiming an upstream side effect succeeded solely because a handler returned.
