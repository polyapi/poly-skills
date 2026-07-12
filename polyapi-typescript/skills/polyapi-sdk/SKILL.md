---
name: polyapi-sdk
description: Use before writing, wiring, syncing, or deploying PolyAPI TypeScript code and the task needs concrete rules for imports, generated namespaces, function metadata, status handling, and repo sync commands.
---

# TypeScript PolyAPI SDK

## Overview

This skill covers the TypeScript-side PolyAPI runtime and toolchain rules that
are easy to break in real repos: imports from `polyapi`, generated namespaces,
entrypoint metadata, status handling, and the build or sync loop used to push
artifact and code changes safely.

The local [`references/REFERENCE.md`](./references/REFERENCE.md) file contains
the concrete examples and command-discovery checklist behind these rules.

## When to Use

- Before writing any PolyAPI TypeScript client or server function
- When wiring TypeScript code to webhook or trigger artifacts
- When changing package, toolchain, build, or sync commands
- When debugging generated type, context, or sync failures
- When reviewing whether code matches the active repo’s PolyAPI runtime pattern

Do not use this skill:
- For general TypeScript coding style with no PolyAPI runtime context
- When a repo has a stronger local SDK guide that intentionally overrides these
  defaults

## Quick Reference

- Import PolyAPI runtime helpers directly from `polyapi`.
- Prefer generated `schemas.*`, `tabi.*`, and existing platform namespaces over
  local replacement types.
- Keep one default async entrypoint per runtime file.
- Keep top-level function metadata aligned with the deployed function name and
  context. Many TypeScript repos use `const polyConfig: PolyServerFunction = …`.
- Use `polyCustom.responseStatusCode` only at explicit webhook boundaries that
  intentionally control the returned HTTP status.
- Use the repo’s existing package manager, build step, and sync or push command.
- Treat PolyAPI as platform-first: generated paths for functions, `vari`,
  `tabi`, schemas, webhooks, triggers, subscriptions, jobs, and other
  constructs exist only after the artefact is deployed and the SDK is
  regenerated.
- When a generated path is missing, ask for approval to deploy the artefact to
  a non-production environment and regenerate the SDK instead of adding local
  typing workarounds.
- After changing TypeScript or artifacts, run the repo’s sync path and relevant
  tests before finishing.
- Treat the pinned `polyapi` package version as infrastructure. Upgrade it
  deliberately, not casually.

## Implementation

Follow [`references/REFERENCE.md`](./references/REFERENCE.md). Pair this skill
with [`../coding-conventions/SKILL.md`](../coding-conventions/SKILL.md) for TS
style rules and [`../artefacts-usage/SKILL.md`](../artefacts-usage/SKILL.md)
for artifact layout and wiring.

## Common Mistakes

- Extracting or re-casting `poly.*` functions instead of calling them directly
- Inventing local interfaces where `schemas.*` already defines the contract
- Changing function name or context in code without updating the matching
  artifacts
- Forgetting the repo’s build step before sync or push in workspace setups
- Adding `.d.ts` shims, `@ts-expect-error`, `as unknown as`, or untyped access
  to bypass missing generated SDK paths
- Upgrading `polyapi` or changing sync commands without checking how the active
  repo is wired
