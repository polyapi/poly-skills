# AGENTS Guide for Dell Boomi to PolyAPI Migration

This file defines the shared rules for agents using the `boomi-to-polyapi`
pack. Keep this file minimal. Detailed analysis and implementation workflows
belong in the task-specific agent files and skills.

## Scope

- Applies when this pack is being used to analyse a Dell Boomi integration and
  plan or implement a PolyAPI TypeScript target.
- Covers shared workspace assumptions, source-of-truth order, and
  non-negotiable migration rules.
- Does not define detailed analysis steps, migration stages, or implementation
  plans.

## Workspace Context

- The active workspace is typically a single repository containing both the
  Boomi source exports and the target PolyAPI TypeScript implementation, for
  example `boomi-integrations/` for Boomi exports and `workflows/src/` for the
  PolyAPI implementation.
- Do not assume exact repo names or folder names; discover them from the user
  instructions and the active workspace.
- Do not hardcode integration names or assume a specific integration is in
  scope until the user explicitly names it or answers the integration-name
  prompt.

## Source of Truth

1. This `AGENTS.md` for shared pack-wide rules
2. Task-specific agent files
   - `specialised_agents/BOOMI_ARCHITECT.md` for Boomi source analysis
   - `specialised_agents/POLYAPI_CODEAGENT.md` for PolyAPI migration and implementation
3. Relevant pack skills under `skills/`
4. Shared PolyAPI skills under:
   - `../polyapi-common/skills/`
   - `../polyapi-typescript/skills/`
5. Target repository conventions and existing examples when implementing
   PolyAPI
6. Selected Boomi source exports and generated analysis artefacts (compact
   evidence, manifests)
7. User instructions in the current conversation

If instructions conflict, the more specific scope wins. If two instructions at
the same scope conflict, prefer the instruction that preserves existing Boomi
behaviour more faithfully.

## Shared Principles

- Preserve behaviour. Do not optimise, redesign, simplify, or modernise Boomi
  behaviour unless the user explicitly asks.
- Do not invent facts. Only describe or implement behaviour supported by
  Boomi source XML, generated analysis artefacts, the approved target design,
  or explicit user instructions.
- No hardcoding. Discover integration names, workflow names, endpoints,
  configs, and file inventories dynamically.
- Never expose secrets. Record secret identity and classification only, never
  secret values.
- Make implicit Boomi behaviour explicit. Process hierarchy, boundary payload
  formats, Map Editor transforms, runtime variables, and dependencies must be
  documented or implemented explicitly.
- Keep task-specific workflow rules out of this file. Put them in
  `specialised_agents/BOOMI_ARCHITECT.md`,
  `specialised_agents/POLYAPI_CODEAGENT.md`, or the relevant skill.

## Task Entry Points

- Use `specialised_agents/BOOMI_ARCHITECT.md` when the task is Boomi source
  analysis or migration-ready manifest generation.
- Use `specialised_agents/POLYAPI_CODEAGENT.md` when the task is PolyAPI
  design validation, migration planning, or implementation.
- Use `README.md` for pack setup, local dependencies, and skill-script
  prerequisites.
- Use `skills/boomi-download-source/SKILL.md`,
  `skills/boomi-compress-source/SKILL.md`,
  `skills/boomi-to-polyapi-conversion/SKILL.md`,
  `skills/naming-conventions-boomi/SKILL.md`, and
  `skills/generate-schemas-boomi/SKILL.md` for Boomi-specific migration
  stages.
- Use the shared PolyAPI skill packs when the task is writing target
  TypeScript code: `../polyapi-common/skills/*` and
  `../polyapi-typescript/skills/*`.

## Security Constraints

- Never read or access `dev.env`, `.env`, `.env.*`, or any file containing secrets or credentials
- Never access files with extensions like `.key`, `.pem`, `.p12`, `.pfx`, `.crt`
- Only operate within explicitly allowed project directories (e.g. `boomi-integrations/`, `workflows/`)
- Do not execute arbitrary shell commands beyond this pack's own scripts and the target repo's sync/test commands
- No outbound network calls unless explicitly approved (e.g. Boomi source download, PolyAPI deployment push)
- Do not access external secret managers (e.g. 1Password, AWS, GCP)
- Never send secrets or sensitive data to the LLM under any circumstance
- Require human approval before modifying CI/CD, dependencies, or deploying to PolyAPI
- Do not persist or store any sensitive data beyond the current session
