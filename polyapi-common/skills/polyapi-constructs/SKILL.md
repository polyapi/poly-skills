---
name: polyapi-constructs
description: Use when you need a language-agnostic explanation of core PolyAPI constructs (schemas, webhooks, triggers, functions, jobs, vari, tabi, canopy) or you need to choose the right construct for a feature.
---

# PolyAPI Constructs

## Overview

PolyAPI implementations are made of a small set of constructs that work together:

- **Schemas** define contracts (request/response shapes, validation boundaries).
- **Webhooks** expose entrypoints.
- **Triggers** connect entrypoints to server functions.
- **Functions** implement the logic.
- **Jobs** run scheduled entrypoints.
- **Vari (Variables)** store config and small runtime state.
- **Tabi (Tables)** store structured/persisted data.
- **Canopy** renders customer apps from an Application JSON (authored through PolyUI).

This skill is the **language-agnostic** “what is it / when do I use it?” reference.

For language- and repo-layout-specific rules (folder structure, artefact JSON conventions, SDK wiring), use the language packs’ `artefacts-usage` skills.

## When to use

Use this skill when:

- You’re onboarding or explaining PolyAPI concepts (especially “Tabi vs Vari”, “Webhook vs Trigger”, “Job vs Webhook”).
- You need to decide which PolyAPI construct to introduce for a new capability.
- You’re reviewing a design and want to sanity-check that the chosen constructs match the intent.
- You’re writing or updating a repo’s root `AGENTS.md` and want consistent definitions.

Do not use this skill for:

- Customer-facing Canopy Application JSON authoring rules — use the Canopy pack skill.
- Concrete artefact file layouts and required fields — use the language pack `artefacts-usage` skills.

## Runtime model (conceptual)

A common execution path is:

- **Schemas → Webhooks → Triggers → Functions**

Where:

- **Schemas** constrain inputs/outputs.
- **Webhooks** receive requests.
- **Triggers** route/bridge execution to a server function.
- **Functions** orchestrate business logic and call downstream systems.

Other entrypoints:

- **Jobs** are scheduled entrypoints (time-based). They typically invoke a server function (directly or via a trigger), often for sync, retention, or cleanup.

Supporting constructs:

- **Vari** and **Tabi** support runtime state/config/data that functions need.

## Quick definitions

| Construct | What it is | Typical use |
| --- | --- | --- |
| Schema | A contract for a payload | Validate webhook requests/responses; document function I/O |
| Webhook | Public/receivable entrypoint | Expose an integration endpoint to the outside world |
| Trigger | Wiring between entrypoint and code | Connect a webhook (or other entry) to a specific server function |
| Server function | Backend business logic | Orchestrate calls, validate inputs, map fields, apply policies |
| Client function | Reusable client-side logic | Shared helpers, parsing/normalization, request building |
| Job | Scheduled entrypoint | Polling, periodic sync, retention cleanup, retries |
| Vari (variable) | Stored value, usually config-like | Secrets/config, small caches, retry policies, feature flags |
| Secret | A sensitive vari | Credentials, API keys, tokens |
| Tabi (table) | Stored structured data | Lookup tables, idempotency keys, workflow state/history |
| Canopy | Config-driven UI runtime | Customer applications defined by Application JSON |

## Decision rules

### Webhook vs Trigger vs Job

- Use a **webhook** when an external system (or user-facing flow) needs to call into PolyAPI via an endpoint.
- Use a **trigger** when you need a stable, explicit wiring layer between an entrypoint and a server function (it makes routing and review easier than “implicit” linkage).
- Use a **job** when the driver is time/schedule rather than an inbound request.

If you’re unsure, look for the “true driver”:

- inbound HTTP/event → webhook
- glue/wiring between entry and server function → trigger
- clock/time → job

### Vari vs Secret vs Tabi

- Use **vari** for configuration, small reference data, feature flags, retry/backoff policies, token caches, and other values that are best treated as “read-mostly” config.
- Use a **secret** (a vari with secrecy) for credentials and sensitive values.
- Use **tabi** for structured, queryable, multi-row data and persisted state that grows over time (idempotency, audit/history, reconciliation state, lookup tables).

If the data changes frequently, grows unbounded, or needs multiple keyed records, it usually belongs in **tabi** rather than **vari**.

### Canopy (Application JSON) vs workflow artefacts

- Use **Canopy** when the deliverable is a **customer-facing app UI** driven by an Application JSON deployed to a Poly environment.
- Use **workflow artefacts** (schemas/webhooks/triggers/functions/jobs/vari/tabi) when the deliverable is runtime logic, integrations, and orchestration.

In practice, many customer projects use both: workflow artefacts implement backend behavior; Canopy config exposes it as UI.

## Where to look next (repo skills)

- For TypeScript workflow repos: `polyapi-typescript/skills/artefacts-usage` and `polyapi-typescript/skills/polyapi-sdk`.
- For Python workflow repos: `polyapi-python/skills/artefacts-usage` and `polyapi-python/skills/polyapi-sdk`.
- For Canopy customer authoring through PolyUI: `polyapi-common/skills/canopy-ui`.
- For interpreting design diagrams that mention constructs: `polyapi-common/skills/design-analysis`.
