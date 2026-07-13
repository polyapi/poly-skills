---
name: boomi-compress-source
description: Produces a compact Boomi evidence pack for later PolyAPI implementation. Use at the start of Boomi analysis before writing migration code.
compatibility: Designed for Dell Boomi exports, Boomi analysis documents, and the TypeScript migration workflow in this repo.
---

# Skill: Compress Source

Use this skill to turn a Boomi export into a compact evidence pack that
implementation work can rely on.

## Required Input

-   Integration name is mandatory.
-   If missing, ask exactly: `Please enter integration name:`
-   Stop until integration name is provided.

## Prerequisite

-   Raw Boomi source files must exist under `boomi-integrations/<integrationName>/raw/`.
-   If raw files are missing, stop and ask the user to run the download stage first.

Run the standard compact-evidence generator script:

`python3 .agents/skills/boomi-compress-source/scripts/generate_compact_evidence.py --integration-name "<integrationName>"`

## When To Use

Use this skill at Stage 2, after source download and before implementation planning.

## Workflow

1. Identify the Boomi project folder under `boomi-integrations/`.
2. Run the compact-evidence generator for the target integration.
3. Review generated outputs under `boomi-integrations/<integrationName>/analysis/`.
4. Validate that branch logic, maps/scripts, profiles, and connectors are represented.
5. **Review runtime configuration** — the generator script extracts
   `processproperty`, `connector-settings`, `crossref`, and all
   `documentproperties` shape variables (DPPs and DDPs) automatically. Review
   the new sections in the generated output: `definedProcessProperties`,
   `connectionSettings`, `crossReferenceTables`, and `documentProperties`.
6. Carry compact evidence forward into implementation planning.
7. Extract and record API boundary contract evidence (flat vs nested envelope)
   for inbound and outbound connectors.
8. If envelope shape is ambiguous from XML/profile evidence alone, request one
   known-good runtime payload example (and optionally one failing example).
9. Produce `<integrationName>_MANIFEST.md` under
   `boomi-integrations/<integrationName>/analysis/` using the canonical structure
   in `BOOMI_ARCHITECT.md`.

## Runtime Configuration — What the Script Extracts

The generator script extracts four runtime configuration sections automatically.
No manual XML reading is required. This section explains what each section
contains so you can interpret the output correctly.

### Boomi Runtime Property Taxonomy

| Output section | Boomi concept | What it holds |
|---|---|---|
| `definedProcessProperties` | Defined Process Property group (`processproperty` component) | Named, typed, labeled properties deployed as a group. `type="password"` properties have `isSecret=true` and no `defaultValue` in the output. |
| `documentProperties.dynamicProcessProperties` | Dynamic Process Property (DPP) | Process-scoped runtime variable. Set by `documentproperties` shapes with `propertyId="process.*"`. Inherits `isSecret=true` when sourced from a password-type Defined Process Property. |
| `documentProperties.dynamicDocumentProperties` | Dynamic Document Property (DDP) | Document-scoped runtime variable. Set by `documentproperties` shapes with `propertyId="dynamicdocument.*"`. Cleared per document. |
| `connectionSettings` | Connection configuration (`connector-settings` component) | Host, URL, driver, username. `hasEncryptedPassword=true` when a password is stored encrypted. Password bytes are never included. |
| `crossReferenceTables` | Cross-reference table (`crossref` component) | Lookup table with all column headers and rows. |

### Recording extracted data in the manifest

When writing the manifest `Runtime Configuration` section, use the extracted JSON
directly — do not re-derive or approximate values. Follow the table format in
`BOOMI_ARCHITECT.md`. Group by: secrets (DPPs and Defined Process Properties with
`isSecret=true`), non-secret config (Defined Process Properties with
`isSecret=false`), DPPs, DDPs, connections, and cross-reference tables.

## Rules

-   Inspect the full available source set before drawing conclusions.
-   Use the owned compact-evidence script under this skill folder.
-   Record missing artifacts and confidence level explicitly.
-   Distinguish profile mapping paths from literal runtime JSON keys.
-   Prioritize runtime-tested payload evidence over profile-path interpretation
    for boundary envelope decisions.
-   Treat condensed analysis as implementation aid, not as replacement for raw
    evidence when conflict appears.
-   Follow canonical structure rules from `BOOMI_ARCHITECT.md`.
-   Never transcribe, log, or include literal secret values (passwords, encrypted
    bytes, tokens) anywhere in analysis output.

## Reference

See `references/REFERENCE.md` for recommended evidence-pack content and
verification guidance.
