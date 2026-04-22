# AGENTS Guide for MuleSoft to PolyAPI Migration

This file defines the shared rules for agents using the `mulesoft-to-polyapi`
pack. Keep this file minimal. Detailed analysis and implementation workflows
belong in the task-specific agent files and skills.

## Scope

- Applies when this pack is being used to analyse MuleSoft source and plan or
  implement a PolyAPI target.
- Covers shared workspace assumptions, source-of-truth order, and
  non-negotiable migration rules.
- Does not define detailed analysis steps, migration stages, or implementation
  plans.

## Workspace Context

- The active workspace usually includes a MuleSoft source repository and a
  target PolyAPI repository.
- Do not assume exact repo names or sibling-folder names; discover them from
  the user instructions and the active workspace.
- Do not hardcode project names or assume a specific integration is in scope
  until the user or active task file establishes it.

## Source of Truth

1. This `AGENTS.md` for shared pack-wide rules
2. Task-specific agent files
   - `specialised_agents/MULE_ARCHITECT.md` for MuleSoft analysis
   - `specialised_agents/POLYAPI_CODEAGENT.md` for PolyAPI migration and implementation
3. Relevant pack skills under `../skills/`
4. Shared PolyAPI skills under:
   - `../../polyapi-common/skills/`
   - `../../polyapi-python/skills/`
   - `../../polyapi-typescript/skills/`
5. Target repository conventions and existing examples when implementing
   PolyAPI
6. Selected MuleSoft project artefacts and generated analysis artefacts
7. User instructions in the current conversation

If instructions conflict, the more specific scope wins. If two instructions at
the same scope conflict, prefer the instruction that preserves existing
behaviour more faithfully.

## Shared Principles

- Preserve behaviour. Do not optimise, redesign, simplify, or modernise
  behaviour unless the user explicitly asks.
- Do not invent facts. Only describe or implement behaviour supported by source
  artefacts, generated analysis artefacts, or explicit user instructions.
- No hardcoding. Discover project names, workflow names, endpoints, configs,
  and file inventories dynamically.
- Never expose secrets. Record secret names only, never secret values.
- Make implicit Mule behaviour explicit. Inputs, outputs, variables,
  dependencies, and XML boundaries must be documented or implemented
  explicitly.
- Keep task-specific workflow rules out of this file. Put them in
  `specialised_agents/MULE_ARCHITECT.md`,
  `specialised_agents/POLYAPI_CODEAGENT.md`, or the relevant skill.

## Task Entry Points

- Use `specialised_agents/MULE_ARCHITECT.md` when the task is Mule analysis or
  migration-ready documentation.
- Use `specialised_agents/POLYAPI_CODEAGENT.md` when the task is PolyAPI
  design validation, migration planning, or implementation.
- Use `README.md` for pack setup, local dependencies, and skill-script
  prerequisites.
- Use `../skills/*/SKILL.md` for Mule-specific extraction, compression, and
  schema workflows.
- Use the shared PolyAPI skill packs when the task is writing target code:
  `../../polyapi-common/skills/*`, `../../polyapi-python/skills/*`, and
  `../../polyapi-typescript/skills/*`.

## Security Constraints

- Never read or access `.env`, `.env.*`, or any file containing secrets or credentials
- Never access files with extensions like `.key`, `.pem`, `.p12`, `.pfx`, `.crt`
- Only operate within explicitly allowed project directories (e.g. `/src`, `/tests`)
- Do not execute arbitrary shell commands, only use an approved allowlist if provided
- No outbound network calls unless explicitly approved
- Do not access external secret managers (e.g. 1Password, AWS, GCP)
- Never send secrets or sensitive data to the LLM under any circumstance
- Require human approval before modifying CI/CD, dependencies, or reading config files
- Do not persist or store any sensitive data beyond the current session
