---
name: generate-overview
description: Use when a PolyAPI workflow or utility is new, its OVERVIEW.md is missing or stale, or changes to functions, artefacts, configuration, or shared helpers alter its runtime behavior.
---

# Workflow overview maintenance

Update the smallest workflow or utility folder that owns the changed behavior.
Resolve its location from the active repository; roots such as `src/` and
`workflows/src/` are both valid. Use its same-folder `OVERVIEW.md` rather than
creating a second guide. Formatting-only edits do not require a rewrite.

## Inspect the actual flow

- Use code and artefacts as primary evidence, tests as confirmation, and existing
  prose as secondary context. Verify documented defaults against implementation.
- Discover entrypoints through the repository's conventions, function metadata,
  and callers. Do not assume a language, file suffix, or fixed function signature.
- Follow client and shared helper logic when it changes validation, branching,
  retries, caching, error handling, state, or external effects. Explain relevant
  behavior instead of leaving those dependencies as black boxes.
- Inspect relevant artefacts: schemas, webhooks, triggers, Vari, Tabi, jobs, AI
  functions/tools, Canopy, subscriptions, and training specs. Also inspect safe
  deployment configuration and scripts when they affect the flow. Resource kinds
  and paths come from the active repo's supported tooling.
- Read safe source and configuration examples only. Never use real environment
  files, SDK credential stores, or customer payloads to populate documentation.
- Distinguish source-verified behavior, local test evidence, and target-dependent
  runtime assumptions. Do not infer deployment from a passing unit test.

## Write what a maintainer needs

Cover relevant items without empty sections:

- Purpose and callable entrypoints, including actual trigger or known caller.
- Input/output contracts, HTTP status behavior, validation, and handled failures.
- SDK dependencies and exact resource contexts, with important client/helper
  behavior explained.
- Configuration names and secrecy levels, injection boundaries, and intended
  enabled state of jobs or streams. Preserve exact non-secret names and verified
  defaults; use placeholders for secret values.
- External effects, retry/idempotency behavior, operational limits, and end states.
- Focused local checks and separately labeled opt-in runtime verification.

For multiple flows, give each entrypoint a `Flow: <name>` section. Include a
Mermaid flowchart when it helps explain branching or multiple resource effects;
a short utility can use prose. Diagrams and text must agree about callers,
decisions, effects, and outcomes. Link relevant implementation and artefact files
with relative Markdown links that resolve from the overview's location.

Use the repository's documented command shell and working directory. Link root
setup and CLI guides instead of copying entire deployment procedures. General
workflow docs should not acquire assumptions from an unrelated customer or host.

## Finish

Verify names, paths, defaults, commands, and every local link. State the checks
actually run and the remaining environment-dependent validation. Do not deploy,
train APIs, invoke AI, or mutate resources to make a documentation claim appear
verified. Those effects require their own authorized scope.

See [the reference](references/REFERENCE.md) for discovery, structure, diagrams,
and verification examples.
