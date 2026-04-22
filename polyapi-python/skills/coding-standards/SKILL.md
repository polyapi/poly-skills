---
name: coding-standards
description: Enforces generic PolyAPI Python error handling, logging, and
  overview-maintenance standards. Use before writing or reviewing server
  functions, client functions, or utilities that need structured errors,
  consistent logs, and up-to-date `OVERVIEW.md` files.
compatibility: Designed for PolyAPI Python work. Examples assume Python 3.12+ and a shared structured logger, but project-specific logger wiring and boundary payloads come from the active repo.
---

# Skill: Coding Standards

## Purpose

Enforce reusable error handling, logging, and overview-maintenance standards
when writing PolyAPI Python code. These patterns should stay stable across
repos even when response envelopes, loggers, or alerting helpers differ.

## When to use

Load this skill before writing any error handling or logging code. Apply it
when reviewing generated code for compliance. Also apply it whenever
behavior-changing work is done under `src/<workflow_name>/` or
`src/utilities/<utility_name>/`.

---

## Core rules

- Catch the most specific exception type you can handle.
- Re-raise with `from error` when adding context.
- Log before returning from handled error paths.
- Order `except` clauses from most specific to least specific.
- Do not swallow unexpected programming errors below the top-level boundary.
- At the top-level boundary, log unexpected failures and convert them into the repo's established error payload and status behaviour.
- Preserve repo-specific alerting or status-setting side effects that existing sibling code already uses.
- Do not log secrets, tokens, or passwords.
- Use DEBUG payload logging only when the payload materially affects branching behaviour.
- After behavior-changing edits under `src/<workflow_name>/`, create or refresh
  that folder's `OVERVIEW.md`.
- After behavior-changing edits under `src/utilities/<utility_name>/`, create
  or refresh that utility folder's `OVERVIEW.md`.
- For new workflow or utility folders, ensure `OVERVIEW.md` exists before
  finishing.
- Formatting-only, comment-only, and non-runtime changes do not require an
  overview refresh.
- Use the `generate-overview` skill for overview creation or refresh work.

## Boundary and logging guidance

- Error return shape is repo-specific. Copy the nearest sibling workflow or utility instead of inventing a new global envelope.
- If the repo sets HTTP status metadata separately from the returned payload, set that metadata before returning.
- Use the repo's shared structured logger interface and prefer a message plus context dict where supported.
- Treat overview freshness as part of the implementation boundary: if behavior
  changed, the same-folder overview must reflect the new behavior before the
  task is complete.

## Reference

See `./references/REFERENCE.md` for specific exception examples, network and
subprocess patterns, logging level guidance, code snippets, and the overview
maintenance checklist.
