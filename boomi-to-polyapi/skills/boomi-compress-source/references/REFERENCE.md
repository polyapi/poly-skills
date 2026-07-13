# Compress Source Reference

## Purpose

Generate a compact Boomi evidence pack that implementation can consume quickly
without losing boundary-contract clarity.

## Command

Run from repository root:

```bash
python3 .agents/skills/boomi-compress-source/scripts/generate_compact_evidence.py \
	--integration-name "<integrationName>"
```

## Inputs

The script reads Boomi raw evidence produced by downloader stage:

-   `boomi-integrations/<integrationName>/raw/<integrationName>.componentMetadata.xml`
-   `boomi-integrations/<integrationName>/raw/<integrationName>.component.xml`
-   `boomi-integrations/<integrationName>/raw/<integrationName>.componentGraph.json`
-   `boomi-integrations/<integrationName>/raw/dependencies/*.component.xml`

## Outputs

-   `boomi-integrations/<integrationName>/analysis/compactEvidence.json`
-   `boomi-integrations/<integrationName>/analysis/compactEvidence.md`
-   `boomi-integrations/<integrationName>/analysis/<integrationName>_MANIFEST.md`

## Manifest Blueprint

The manifest must follow the canonical Stage 2 structure from
`BOOMI_ARCHITECT.md`.

Required major sections:

1. summary heading (preferred `## Title and Summary`; compatibility allows
   `## 1. Title and Summary`, `## Summary`, or `## Project Summary`)
2. `## Table of Contents` or `## Contents`
      - TOC should start at 1 with `Common Elements`; do not include `Title and
         Summary`
3. common elements heading (preferred `## 2. Common Elements`; compatibility
   allows `## Common Elements`)
4. integration flows heading (preferred `## 3. Integration Flows`;
   compatibility allows `## Integration Flows`)
5. Optional outbound section when applicable
6. Gaps section (`Gaps and Ambiguities` or `Analysis Gaps`)

For each flow under `## 3. Integration Flows`, include these subsections:

-   business purpose
-   trigger or entry point
-   flow implementation details
-   sequence diagram
-   request or trigger input
-   response or completion output
-   authentication and authorisation
-   validation
-   routing logic
-   transformation and mapping
-   business logic and rules
-   downstream integrations
-   error handling
-   operational notes

Each flow must also include a numbered step-by-step explanation.

## Verification

Confirm the following before implementation planning:

1. Both compact evidence files exist and are non-empty.
2. Root process steps are represented with shape type and routing info.
3. Connector operations and status expectations are visible.
4. Map/profile artifacts are represented where available.
5. Manifest structure validation passes.
6. Missing components are called out explicitly in warnings or gaps.

## Required Analysis Notes

During playback, include:

-   payload envelope evidence and confidence source
-   status-code branches and error paths
-   map/script/decision behavior in execution order
-   unresolved gaps that require user confirmation
