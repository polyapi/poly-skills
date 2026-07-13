---
name: generate-schemas-boomi
description: Builds JSON Schema guidance from Boomi profiles, operations, XML samples, or JSON samples. Use when a Boomi project needs explicit request or response contracts for PolyAPI artifacts.
compatibility: Designed for Boomi profile analysis and TypeScript PolyAPI webhook/schema artifacts.
---

# Skill: Generate Schemas

Use this skill when the Boomi source contains enough contract information to derive PolyAPI request and response schemas.

This skill is specific to Boomi-to-PolyAPI contract derivation and produces JSON Schema for PolyAPI artifacts.

## When To Use

Use this skill when you have:

-   Boomi profiles
-   operation definitions
-   XML or JSON samples
-   previously written Boomi analysis that already captures payload shape

## Rules

-   Prefer the strongest available contract source: explicit Boomi profile first, then operation detail, then trustworthy examples.
-   **Always read the raw XML profile file directly** when deriving request or response schemas. The compact evidence and manifest summarise orchestration and document-property *sources*, not the full profile structure. They are insufficient for schema derivation.
-   To locate the raw profile: find the `fromProfile` or `toProfile` ID in the map evidence inside `compactEvidence.md` or `compactEvidence.json`, then read `boomi-integrations/<integrationName>/raw/dependencies/<profileId>.component.xml`.
-   **Do not infer or invent fields from document property names.** Document properties (DPP/DDP) name fields that were *read from* a profile; they do not list all fields in that profile, and they omit required flags, data types, cardinality, and nesting structure. Reading them as a substitute for the raw profile will produce an incomplete and partially invented schema.
-   Resolve API boundary envelope explicitly (flat vs nested) from operation/runtime evidence before finalizing schema shape.
-   Preserve field names, cardinality, and required-vs-optional distinctions where the source confirms them.
-   Mark uncertain fields as inferred.
-   Do not invent a loose catch-all schema to get the webhook written quickly.
-   Do not convert profile path segments into mandatory JSON wrapper keys unless runtime evidence confirms those wrappers are literal payload keys.
-   If profile paths include grouping nodes (for example `users/Object/...`) but boundary evidence shows flat JSON, generate the flat schema and document the mapping-path distinction.
-   Translate the final contract into JSON Schema suitable for `artifacts/schemas/` and webhook payload fields.

## Role Boundaries

-   This skill is analysis-first guidance for deriving JSON Schema from Boomi evidence.
-   Reuse existing `artifacts/schemas/*.json` when compatible, and only introduce new schema files when the contract requires it.

## Output

The result should be schema content that can be used in:

-   `artifacts/schemas/*.json`
-   webhook request payload definitions
-   webhook response payload definitions
