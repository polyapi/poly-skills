# Workflow overview reference

## Scope and discovery

Choose the existing workflow or utility folder that owns the behavior, such as
`<workflow_root>/message_of_the_day/` or `<workflow_root>/utilities/common/`.
Create or update `OVERVIEW.md` there. Do not create empty deployment, script, or
artefact folders just to match an example tree.

Read applicable project instructions and conventions, then inspect:

1. Entrypoint code and function metadata under the configured discovery paths.
2. Webhooks/triggers, jobs, subscription destinations, and known SDK callers.
3. Client and helper behavior affecting validation, branching, loops, retries,
   caching, state, error translation, or external I/O.
4. Relevant schemas, Vari, Tabi, AI/tool bindings, Canopy configuration, and specs.
5. Focused tests and checked-in commands confirming the intended behavior.

Use the language and naming patterns the project actually deploys. Server
entrypoints normally define flows; client-only or utility folders can describe
their callable surface and known consumers. Do not invent a deployed trigger
because none is present. Label an inferred caller or unknown setup explicitly.

Treat the current overview as navigation, not proof. Inspect supported source
and configuration examples; exclude environment files, credential stores,
private keys, generated caches, and customer data. A generated SDK contract may
be useful evidence, but its credentials are not.

## Suggested structure

Adapt to the existing overview; retain sections that help maintainers. For a
folder with several entrypoints, use a `Flow: <name>` section for each materially
different flow. Avoid duplicate boilerplate and empty headings.

| Section | Evidence to include when relevant |
| --- | --- |
| Purpose and entrypoints | Callable name/context, source links, webhook/trigger or caller |
| Contracts | Inputs, outputs, validation, response status, error envelope |
| Behavior | Important decisions, client/helper logic, external calls, persisted state |
| Resources and configuration | Artefact links, exact contexts, config names, secrecy/injection, enabled state |
| Operations | External effects, retry/idempotency, stream recreation limits, dependencies |
| Verification | Existing local check commands and separate opt-in runtime checks |

For utility functions, describe meaningful helper behavior without fabricating a
webhook or server wrapper. When shared behavior affects a consumer's contract,
update the relevant consumer overview too, limited to that changed behavior.

## Diagrams and flow details

Use a Mermaid flowchart for nontrivial branches or multi-resource flows. Small
utilities can be clearer as prose or a table. Expand client/helper decisions that
affect outcomes; do not diagram every assignment or formatting step.

A useful chart includes:

- actual trigger or caller entry nodes;
- important validation and business decisions;
- relevant Vari/Tabi, API, database, or other external operations;
- handled error paths and final outcomes.

Use simple node IDs, short labels, and valid Mermaid syntax. Give decisions
explicit labeled outcomes (`yes`/`no` for Boolean choices, appropriate labels for
multi-way results). Do not force multi-way logic into a false binary or omit an
error path to simplify the chart. Keep implementation detail in the prose.

For each significant step, explain its purpose, function/resource identity when
known, important rules and failures, and clickable source/artefact links. An
inferred caller has no implementation link to invent. The chart and text should
describe the same flow and end states.

## Links and commands

Resolve relative Markdown links from the overview location, not the repo root.
For example, a workflow overview can link to `./server/process_event_sfx.py`
only if that file exists. A deeply nested utility needs more `../` segments for
a root README link. Check the actual filesystem rather than copying link depth.

Find commands in the maintained README, CLI help, Makefile, or package scripts.
State their working directory and use the project's documented shell. Separate:

- local formatting, lint, unit, and artefact validation;
- generation/preview that needs a configured target;
- opt-in runtime checks or mutations that need explicit authorization.

Link setup/CLI guides instead of duplicating secrets setup or full deployment
procedures. Use placeholders for config names/values; no region or customer is
implicitly the default target.

## Evidence and finishing checks

Describe source behavior as source behavior. A mocked SDK call proves its local
arguments and result handling, not live SDK generation, authentication, SECRET
resolution, remote build, or deployment. Label unperformed checks accurately.

Before finishing, confirm:

- the smallest owning folder has one maintained `OVERVIEW.md`;
- functions, contracts, triggers, and important helper behavior match current code;
- resource identities, secrecy levels, and enabled states match checked-in artefacts;
- diagram decisions/effects/outcomes agree with the implementation and prose;
- local links and documented commands resolve in the target repository;
- assumptions and remaining target-dependent checks are explicit;
- no deployment or mutation was performed solely to manufacture documentation evidence.
