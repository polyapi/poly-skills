---
name: polyapi-implementation-principles
description: Use when planning or reviewing non-trivial PolyAPI repo implementation changes that affect workflow architecture, artefacts, SDK wiring, security boundaries, or deployment readiness.
---

# PolyAPI Implementation Principles

## Overview

Use this skill as shared, non-personal guidance for architecture-sensitive
PolyAPI repo work. Pair it with language-specific skills for exact SDK, naming,
artefact, logging, and deployment rules. Load it only when a change can alter
workflow behavior, platform contracts, persistent state, security boundaries,
or release readiness.

## When to Use

Use when planning a new PolyAPI workflow, migration slice, cross-file feature,
runtime refactor, or readiness review involving schemas, webhooks, triggers,
functions, jobs, vari, tabi, Canopy, generated SDK usage, or deployment.

Do not use for formatting-only edits, typo fixes, isolated prose changes,
personal workflow setup, local credential wrappers, local runtime paths,
production operator runbooks, or incident procedures.

## Core Principles

| Principle | Rule |
| --- | --- |
| Preserve checked-in behavior | Use executable code, checked-in artefacts, tests, and active `AGENTS.md` as source of truth. Do not redesign unless explicitly asked. |
| Keep contracts aligned | Move schemas, webhooks, triggers, metadata, SDK types, implementation, and tests together when behavior changes. |
| Prefer platform constructs | Use generated `schemas.*`, `tabi.*`, `poly.*`, `vari.*`, and existing platform namespaces unless compatibility requires a local replacement. |
| Choose the right state primitive | Use `vari` for config/secret references/small values, secret vari for credentials, `tabi` for persisted rows, and `jobs` for scheduled lifecycle work. |
| Make boundaries explicit | Validate untrusted input near webhooks, external APIs, files, env/config, generated SDK boundaries, and persisted state. |
| Avoid guessy helpers | Do not add data-shape helpers that guess alternative field names when the contract or upstream payload shape is known. |
| Keep secrets out | Artefacts may record secret names, not values. Logs must mask credential-like keys and avoid request/response bodies at INFO. |
| Keep changes reviewable | Inspect comparable maintained workflows before inventing patterns. Add shared utilities only when they remove real cross-workflow duplication. |
| Verify the active path | Discover build/generate/sync/deploy/test commands from checked-in files. Run relevant checks or report exact gaps. |

## Planning Checklist

- What behavior changes, and what behavior must be preserved?
- Which PolyAPI constructs are involved?
- Which schemas, artefacts, functions, generated types, and tests move
  together?
- Which data is config, secret, persisted table state, or scheduled lifecycle
  state?
- Which comparable checked-in workflow proves the intended pattern?
- Which commands validate this change in the active repo?

## Stop Conditions

Stop and ask before proceeding when:

- Requested behavior conflicts with checked-in source-of-truth artefacts.
- The change needs secret values, local credential wrappers, or raw environment
  files.
- The change would alter deployment, dependencies, CI, or production operation
  rules without explicit approval.
- The required runtime contract cannot be inferred from code, artefacts, tests,
  or user instructions.
