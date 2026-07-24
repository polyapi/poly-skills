---
name: tabi
description: Use when designing, creating, querying, reviewing, or maintaining PolyAPI Tabi tables, generated SDK row operations, pagination, upserts, persisted workflow state, lookup data, idempotency stores, or retention jobs.
---

# Tabi

## Overview

Tabi is PolyAPI's managed PostgreSQL-backed table service for structured,
queryable, multi-row data that persists across workflow executions. Model
filterable fields as top-level columns, use the generated SDK for row
operations, and define retention before data can grow without bound.

## Required Intake

- Inspect the target repo's checked-in Tabi artefacts and generated SDK usage.
- Resolve the exact generated `tabi.<context>.<table>` path; do not invent it.
- Use the connected environment's Swagger or `/swagger-json` for the current
  table-management contract.
- Read [references/tabi-reference.md](./references/tabi-reference.md) before
  creating or changing a table, implementing row operations, or reviewing
  platform limits.

## When to Use

| Need | Prefer |
| --- | --- |
| Secret or credential reference | Secret Vari |
| Small config, feature flag, retry policy, or small token cache | Vari |
| Many keyed rows, filtering, idempotency state, or audit history | Tabi |
| Scheduled row cleanup or lifecycle processing | Job plus Tabi |

Do not use Tabi for credentials, single-execution scratch data, or as a
replacement for an authoritative downstream system.

## Workflow

1. Define writer, readers, stable lookup key, expected volume, retention, and
   owner.
2. Model queryable fields as top-level columns; use `jsonb` for payload storage.
3. Create or update the table through Manage Tabi Tables or Swagger using a
   reviewed `CreateTableDto`/`UpdateTableDto` payload.
4. Regenerate the project SDK after contract changes:

   ```fish
   npx poly generate
   ```

5. Import `tabi` from `polyapi` and use the exact generated path. Prefer the SDK
   over direct REST.
6. Keep artefact, workflow code, tests, and any retention job aligned.

## Non-Negotiable Rules

- Tabi owns `id`, `createdAt`, and `updatedAt`; do not redefine or drop them.
- A column's `schema` supplies generated-SDK typing and documentation, not
  runtime database validation.
- Promote every field that must be filtered or ordered out of `jsonb` into a
  top-level column.
- Unique constraints are per-column and allow multiple `NULL` values. Upsert
  against one unique column; composite constraints and foreign keys are not
  supported.
- Schema updates may add or drop columns. Do not rename columns or change type,
  nullability, or default. Unique may be added but not removed.
- `selectMany` returns at most 1,000 rows. Offset pagination requires a stable,
  deterministic `orderBy`, normally `{ id: "asc" }`.
- Scope every update and delete with explicit `where`; omission targets the
  full table. Count with the same filter before broad mutations.
- Store only payload slices needed for lookup, routing, replay, or audit. Never
  store secrets or log unrestricted row payloads.

## Artefact Placement

- TypeScript: `src/<workflow>/artifacts/tabi/`
- Python: `src/<workflow>/artefacts/tabi/`

Table creation artefacts define columns; they do not contain seed `rows`.

## Review Checklist

- Are writer, readers, ownership, lookup keys, volume, and retention explicit?
- Do artefact, generated path/types, workflow code, and tests agree?
- Are query fields top-level, pagination ordered, mutations scoped, and upserts
  keyed by one supported unique column?
- Are unsupported schema changes, composite constraints, foreign keys, secrets,
  and unnecessary customer payloads excluded?

## Common Mistakes

- Treating JSON Schema as PostgreSQL validation.
- Querying inside `jsonb` or paginating without deterministic `orderBy`.
- Running update/delete without `where` or creating a table without retention.
