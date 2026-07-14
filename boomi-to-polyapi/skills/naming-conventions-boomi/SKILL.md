---
name: naming-conventions-boomi
description: Use when naming or reviewing Boomi-to-PolyAPI workflows, artifacts, contexts, and shared utilities to keep migration outputs consistent.
---

# Skill: Naming Conventions

Use this skill to keep TypeScript workflow names, artifact names, and PolyAPI contexts coherent across a Boomi migration.

## Core Rules

-   Contexts must start with `POLYAPI_NAMESPACE`.
-   Integration contexts should reflect business domain and flow purpose, for example `<namespace>.finance.ap`.
-   Shared utility contexts should live under a utilities namespace, for example `<namespace>.utilities.logging`.
-   Server and client metadata JSON should use the same basename as the `.ts` file beside it.
-   Webhook and trigger names should stay obviously paired.
-   Use the repository's established TypeScript-local naming style; current examples use consistent camelCase filenames.

## Naming Guidance

-   Integration folder: `workflows/src/<integrationName>/`
-   Server function: `server/createInvoice.ts` and `server/createInvoice.json`
-   Client function: `client/buildInvoicePayload.ts` and `client/buildInvoicePayload.json`
-   Webhook: `artifacts/webhooks/invoiceWebhook.json`
-   Trigger: `artifacts/triggers/invoiceTrigger.json`
-   Variable: `artifacts/vari/apiCredentials.json`
-   Job: `artifacts/jobs/syncInvoices.json`
-   Table: `artifacts/tabi/invoiceLookup.json`

## Rules

-   Do not carry over unrelated legacy prefixes, slugs, or suffixes.
-   Do not create multiple near-identical contexts when one shared context is sufficient.
-   Do not use legacy naming rules from older non-Boomi projects as the default for new work.
