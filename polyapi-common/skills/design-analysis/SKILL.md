---
name: design-analysis
description: Explains how to analyse PolyAPI design diagrams and recover missing behaviour from source artefacts. Use when the user provides architecture images, screenshots, or high-level design diagrams.
---

# Skill: Design Analysis

## Purpose

Rules for interpreting PolyAPI design diagrams provided as images or screenshots. Diagrams define the target architecture but are typically high-level — this skill tells you how to read them without guessing incorrectly.

## When to use

Load this skill as soon as the user provides a design diagram, before
implementation planning begins.

---

## Core rule

Diagrams define **what to build**. They do not show all internal behaviour.

Missing low-level detail **does not mean the behaviour should be removed**.
Recover it from source artefacts or approved upstream-system behaviour.

When the diagram is not explicit enough to choose the correct PolyAPI construct or function split, the agent must ask the user for clarification during Stage 2 instead of guessing.

---

## Colour semantics and construct mapping

| Colour | Meaning |
|---|---|
| Red | Entry artefact: webhook endpoint, trigger, or job |
| Blue | Server function |
| Yellow | Client function or client-side logic block |
| Green | Variable, secret, or Tabi |
| Grey | External source or target system |
| Pink / light pink | Existing PolyAPI function, either OOB or manually trained |

### Red boxes

Red boxes are not business logic. They represent the mechanism that starts execution.

They may mean:

- a webhook endpoint / API endpoint
- a trigger wired to a webhook
- a job / scheduler entrypoint

Use nearby labels and arrows to decide which one it is:

- scheduled or time-based language usually means a job
- public URL or API semantics usually means a webhook endpoint
- a routing bridge between an entrypoint and a server function usually means a trigger

If it is still not clear which artefact is intended, ask the user before deciding.

### Blue boxes

A blue box is a server function.

Treat it as the main orchestration or boundary logic for that step unless the user specifies otherwise.

### Yellow boxes

A yellow box is a client function or logic that should live in client-side reusable code.

Important:

- a yellow box does **not** always mean exactly one client function file
- one yellow box may become one client function, several client functions, or logic folded into a nearby client function
- the correct split depends on the design and the surrounding implementation pattern

If the correct split is not clear, ask the user for clarification instead of forcing a one-box-to-one-file mapping.

### Green boxes

A green box is one of:

- a variable
- a secret
- a Tabi

Use the following default decision rules:

- use a secret for credentials, tokens, keys, or other sensitive values
- use a variable for normal runtime configuration or small structured state/config data
- use a Tabi only when the design clearly implies lookup-table style data or reference data that would be awkward or poor practice to model as a variable

If it is not possible to infer which one is intended, ask the user.

Do not force a Tabi when a variable is the cleaner solution. Tabis are harder to implement, use, and maintain, so prefer a variable unless a variable would clearly be the wrong construct.

### Grey boxes

A grey box represents an external source or target system.

Assume it is outside the PolyAPI implementation boundary unless the user says otherwise.

### Pink / light pink boxes

A pink or light pink box represents a PolyAPI function that should already exist:

- either OOB in the PolyAPI SDK
- or manually trained and intended for reuse

Do not reimplement a pink-box capability by default. First try to determine whether the function already exists and should be reused. If reuse cannot be confirmed, raise it during playback and ask the user.

### Reference artefacts

If a box is explicitly labelled as a document, script, spec, compressed source, or source integration manifest, treat it as a reference artefact even if its colour is pale or grey-toned. It is input context, not a deployable PolyAPI component.

---

## Arrow semantics

| Arrow | Meaning |
|---|---|
| Solid | In-scope flow |
| Dashed | Context only / out of scope |

Arrow labels describe important behaviour — do not ignore them.

Where a branch is numbered, treat the numbers as execution order or call sequence from the same upstream component unless the diagram notes say otherwise.

---

## Boxes and notes

- Diagram text and box labels may contain agent guidance — read all text carefully.
- Notes on the diagram are requirements, not decoration.
- A box without arrows may represent a shared utility used across components.
- A box labelled `utility:` or grouped under text such as `Utilised by all functions` should usually be treated as a shared reusable utility.
- External systems shown at the edge of the diagram are outside the code the agent should generate.

---

## What to do when detail is missing

If the design is high-level and omits internal behaviour:

1. Recover the missing behaviour from the source artefacts.
2. Flag the gap during planning playback as a **high-level diagram omission**.
3. Propose how to fill the gap and wait for user confirmation.

Do not silently implement reduced behaviour because the diagram omitted it.

## What to do when construct choice is ambiguous

If the diagram is not clear enough to decide any of the following:

- webhook vs trigger vs job
- one client function vs several client functions
- variable vs secret vs Tabi
- reuse existing pink-box PolyAPI function vs implement new code

then:

1. state the most likely interpretation
2. state the reasonable alternative(s)
3. explain what implementation choice would change
4. ask the user to confirm before coding

Do not guess when the ambiguity changes the deployed artefacts or implementation shape.
