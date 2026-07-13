---
name: boomi-download-source
description: Download Boomi integration XML components directly from the Boomi API into boomi-integrations/<integrationName>/raw for migration analysis.
compatibility: Designed for Dell Boomi API exports and repository-local Boomi source preparation.
---

# Skill: Download Boomi Source

Use this skill to fetch Boomi integration XML files from the Boomi API before
compact evidence generation.

## Required Input

-   Integration name is mandatory.
-   Folder name is mandatory.
-   Environment file path is mandatory for source download. Use
    `./workflows/dev.env`, or another human-provided env file path.
-   If missing, ask exactly: `Please enter integration name to download:`
-   Then ask exactly: `Please enter Boomi folder name or folder path:`
-   Then ask exactly: `Please enter environment file path:`
-   When asking for the environment file path, state that the agent will not
    read, parse, print, summarize, or inspect the file under any circumstances;
    the path is only passed as an argument to this skill script so the runtime
    script can load credentials.
-   Stop until integration name, folder name, and environment file path are
    provided when source download is required.

## When To Use

Use this skill at the start of Stage 1 analysis, before source compression and
playback.

## Workflow

1. Ensure required values are already present in the human-managed
   `./workflows/dev.env` env file. Agents must not
   directly read, parse, print, summarize, or inspect env files. The downloader
   may load the provided env file path at runtime and validates required keys:

    - `BOOMI_ACCOUNT_ID`
    - `BOOMI_USERNAME`
    - `BOOMI_API_URL`
    - `BOOMI_API_TOKEN`

    Optional: `BOOMI_API_TIMEOUT_SECONDS` (defaults to `30`)

2. Run the downloader with deterministic flags (`--clean-first` and explicit
   timeout or `BOOMI_API_TIMEOUT_SECONDS`).
3. Verify expected raw output files exist under
   `boomi-integrations/<integrationName>/raw/`.
4. Stop and investigate if metadata lookup fails or graph output is missing.

## Command

```bash
python3 .agents/skills/boomi-download-source/scripts/download_integration_xmls.py \
  --integration-name "<integrationName>" \
  --folder-name "<FolderName>" \
  --env-file "<envFilePath>" \
  --timeout-seconds 60 \
  --clean-first
```

## Outputs

-   `boomi-integrations/<integrationName>/raw/<integrationName>.componentMetadata.xml`
-   `boomi-integrations/<integrationName>/raw/<integrationName>.component.xml`
-   `boomi-integrations/<integrationName>/raw/<integrationName>.componentGraph.json`
-   `boomi-integrations/<integrationName>/raw/dependencies/<componentId>.component.xml`

## Rules

-   Do not commit credentials or inline tokens in command history files.
-   Keep raw Boomi XML output deterministic for repeat analysis runs.
-   Treat downloaded component XML files as source-of-truth behavior evidence.
