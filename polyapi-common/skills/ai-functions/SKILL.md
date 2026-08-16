---
name: ai-functions
description: Use when designing or implementing a PolyAPI solution where a function's inputs and outputs can be defined, but its real-world language, formats, exceptions, combinations, or usage scenarios cannot yet be enumerated reliably; also use when creating, updating, reviewing, or debugging Flow AI Function artefacts.
---

# AI Functions

## Core mental model

Treat an AI Function as a stable function contract with an adaptable LLM implementation.

Determine the purpose, inputs, output schema, permitted tools, and safety boundaries upfront. Do not require the team to predict every phrase, document layout, combination, exception, or reasoning path before shipping. Let the LLM handle that initially unknown implementation space behind the contract.

Ask the central question:

> **If we implement this logic as deterministic code now, do we know enough for it to work across the real scenarios, or will each newly discovered scenario force another code change?**

Distinguish an implementation-speed problem from a knowledge problem. A coding agent can generate known rules quickly; it cannot make unobserved scenarios known. If the number and shape of those scenarios are highly uncertain, “just code it” may only automate guessed behavior. The elapsed time from first implementation to genuinely stable coverage is then undefined, however fast the first code is produced.

Use production logs to turn hypothetical scenarios into observed scenarios. As evidence accumulates, use LOOP to replace recurring behavior with deterministic code, retain AI only for the unresolved long tail, or replace the AI implementation completely—without changing the contract used by the rest of the solution.

The value is therefore not merely “AI handles ambiguity.” It is faster time to market plus requirements discovery: ship a useful bounded capability before its complete decision logic is knowable, then optimize from real usage rather than guesses.

## Find the right boundary

Ask in order:

1. **Can the contract be defined now?** Specify meaningful inputs and a strict, testable output. If not, clarify the capability first.
2. **Would code written now really be stable?** Ask whether it covers the real scenario space or only the cases currently imagined.
3. **How unknown is that scenario space?** Consider formats, phrasings, combinations, exceptions, and semantic judgments not yet observed. The more each discovery would require another branch, parser, or deployment, the stronger the AI Function case.
4. **Is this a knowledge problem or only an implementation problem?** Use a coding agent and ordinary code when the rules are known. Use an AI Function candidate when generating code faster still leaves coverage unknowable.
5. **Can failures be contained?** Validate outputs and keep authorization, persistence, money movement, destructive operations, and other consequential actions deterministic.
6. **Can this implementation evolve independently?** Draw a narrow boundary that LOOP could later replace or split without redesigning the solution.

Prefer several focused AI Functions when capabilities have different contracts or are likely to become deterministic at different rates. Never hide an entire workflow inside one massive prompt that calls many tools.

## Concrete boundaries

| Solution | AI Function boundary and initial value | Keep deterministic |
|---|---|---|
| Supplier integration | Input: document and supplier context. Output: `PurchaseOrderDraft`. Handle unseen layouts, labels, omissions, and line-item descriptions without building per-supplier parsers first | OCR, supplier/SKU validation, totals, duplicate detection, ERP creation |
| Integration operations | Input: execution evidence. Output: `FailureDiagnosis`. Interpret unfamiliar provider errors and nested causes before a complete error catalogue exists | Retry policy, redaction, routing, alerts, remediation |
| SaaS onboarding | Input: requirements text and product constraints. Output: `ConfigurationDraft`. Cover customer language and option combinations not anticipated during design | Schema/policy validation, permissions, persistence |
| Record reconciliation | Input: unmatched record and candidates. Output: `MatchProposal`. Handle spelling, address, naming, and identifier variations after exact matching fails | Candidate retrieval, thresholds, merge approval and execution |
| Claims or case intake | Input: claimant details and incident material. Output: `ClaimAssessment`. Structure mixed notes, emails, OCR, contradictions, and missing facts behind one stable output | Eligibility rules, risk policy, claim decisions, storage |
| Operational application | Input: exception evidence. Output: `ExceptionAssessment`. Summarize novel exception combinations and propose next steps before their recurring patterns are known | Calculations, state transitions, approvals, side effects |

Do not use an AI Function for exact field mappings, formulas, authorization, known validation rules, state machines, or other behavior whose cases and expected results can already be expressed reliably in code and tests.

## Mandatory approval gate

Never introduce or materially expand an AI Function without the user's explicit, informed approval.

Before writing or modifying its code or artefact:

Give a brief, objective approval request—normally two or three sentences, never a design memo. State the bounded contract and placement, the material unknowns that make code unstable or speculative now, and the main deterministic safety boundary. Mention LOOP evolution, cost, latency, or security only when material to the decision. Then ask: **May I implement this AI Function?** Stop and wait.

Use this shape:

> I propose `[name]` at `[boundary]`. Input: `[inputs]`. Output: `[output]`. `[Unknown scenario space]` makes deterministic coverage unstable now; `[consequential behavior]` remains in code, and observed cases can later drive deterministic replacement. May I implement it?

Prefer substance over completeness. Do not repeat the solution architecture, enumerate every field, provide implementation steps, or front-load a risk register unless the user asks.

Implementation instructions, urgency, or an earlier mention of AI Functions do not count as approval after this proposal. Do not scaffold or implement before approval. Reviewing or diagnosing an existing AI Function needs no approval.

## Implement for evolution

After approval, inspect a comparable artefact and confirm the namespace. Define focused arguments, a precise prompt and input template, and a strict output schema. Use tools only for authoritative facts. Keep the deterministic shell responsible for input preparation, output validation, policy, fallbacks, and side effects.

Keep prompt content directly in the AI Function artefact's `systemPrompt` field by default. Use `systemPromptVariable` only when the user explicitly requests externally managed prompt content; never create a vari solely for prompt storage by default. Continue to use vari references for secrets and tool credentials.

Make logs useful for later optimization: preserve the contract version, inputs and outputs allowed by security policy, validation results, human corrections, failures, latency, and cost. Never log secrets. Review observed cases before deciding what LOOP should make deterministic; do not optimize from imagined patterns.

Use portable Flow references: `functionName` with `functionContext`, and `variableName` with `variableContext`. Never emit environment-specific `id`, `variableId`, `systemPromptVariableId`, `toolFunctionIds`, or `contextName`.
Function reference contexts do not need to start with `POLYAPI_NAMESPACE`: they may identify any exact environment, tenant, or public function accessible to the target PolyAPI environment. Keep variable references and the AI Function artefact's own `context` inside `POLYAPI_NAMESPACE`.

Read [references/examples.md](references/examples.md) before proposing or implementing an AI Function. It contains complete approval proposals, evolution plans, and valid Flow artefacts.
