# Python Flow Operations

## Discover the Installed Interface

Read project instructions and check help using the existing environment. These
examples describe the current Python Flow template:

```bash
uv run --locked python -m cli.operations delete-content --help
uv run --locked python -m cli.operations logs --help
```

The project's loaded shell helper also exposes `flow delete-content` and
`flow logs`. If Flow is absent, discover the repo's supported tooling instead
of installing another CLI or inventing options. Keep the pinned native SDK.

Use the selected `ENVPATH` and configured connection. Flow verifies the
`TARGET_ENV_ID` pin declared in that env file; exporting a pin alone is
insufficient. Let the CLI load credentials and handle OTP. Preserve target
identity, branch and production safeguards, and keep keys out of commands,
reports and log files.

## Preview and Delete Resources

Use an owned namespace in place of `demo`. This queries server metadata and
previews cleanup without deleting anything:

```bash
uv run --locked python -m cli.operations delete-content --types api-functions,schemas --context demo.crm
```

Context matching is exact by default: `demo.crm.contacts` and
`demo.crm.shared` are preserved. Add `--include-children` only when the intended
scope includes these dot-separated descendants. Recursive spec-folder
discovery during training does not change deletion scope.

When existing user authorization covers this target, types and exact scope:

```bash
uv run --locked python -m cli.operations delete-content --types api-functions,schemas --context demo.crm --apply
```

Review the preview and satisfy the separate exact `DELETE` confirmation.
Training, log retrieval or advice alone grants no cleanup authorization;
reuse authorization already given for cleanup rather than asking again for
the same scope.

| Behavior | Operational meaning |
| --- | --- |
| No `--apply` | Preview only; deletion has no `--dry-run` flag in this interface |
| `--types` | Comma-separated kinds, such as `api-functions,schemas,variables` |
| Exact context | Descendants require `--include-children` |
| Namespace ownership | Accessible shared resources are not automatically owned |
| 404 readback | Every DELETE is followed by verification; uncertainty stops the command |

Canonical kinds are `api-functions`, `client-functions`, `server-functions`,
`ai-functions`, `schemas`, `variables`, `webhooks`, `triggers`, `jobs`, `tables`
and `subscriptions`; verify local help. Jobs and triggers qualify only when
every referenced server function is known and in scope. Selected dependents
are removed before functions and schemas. Context selection does not infer
a cascade into other contexts: inventory related resources and include only
authorized cleanup. Preview metadata without fetching variable values.

Deletion changes remote state, not checked-in artefacts. Flag local definitions
that a future push or training run could recreate; edit those files only when
permanent local removal is also within the user's requested scope.

If any request or readback fails, stop and inspect remaining state before an
authorized retry. When local SDK absence matters, regenerate using the repo's
documented native SDK command on the same target and verify deleted exports
are absent. Report remote deletion separately from local SDK state.

## Read Server-Function Logs

Resolve the actual server-function ID from an authorized metadata listing or
the repo's existing registry; a function name or SDK path is not an ID.

```bash
uv run --locked python -m cli.operations logs SERVER_FUNCTION_ID --logs-page 1 --logs-page-size 500 --limit 500 --keyword trace-123
```

This reads one page without invoking or deploying the function. `--page` and
`--page-size` are aliases for the shown pagination flags. Limit defaults to
page size. `--keyword` is a text filter rather than a structured trace-ID
selector; an empty filtered page does not prove no invocation occurred.
Inspect pagination metadata before requesting additional pages. `--raw` returns
the original response if formatting hides needed diagnostic information.

Client-function logs appear within the calling server-function execution.
Reads do not need a write OTP, but Python Flow still verifies the target pin
and applies its project preflight checks. Logs may contain credentials or
customer payloads: retrieve bounded, relevant pages and redact sensitive
content before reporting or saving it. Report function, target, page/filter,
timestamps and relevant events. A handler's successful return alone does not
prove an upstream side effect succeeded.
