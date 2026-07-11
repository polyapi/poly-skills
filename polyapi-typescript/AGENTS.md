# AGENTS Guide for PolyAPI TypeScript

Shared repo-wide rules for agents working inside a PolyAPI TypeScript
repository. Keep this file focused on source-of-truth order, workflow model,
and skill entry points. Detailed implementation guidance belongs in the local
skills.

## Scope

- Applies to all work started from a PolyAPI TypeScript repo.
- Covers shared source-of-truth order, workflow model, repo-wide principles,
  and skill entry points.
- Does not duplicate detailed SDK, naming, artefact, or project-specific
  implementation rules.

## Source of Truth

1. Direct user instructions, unless they conflict with execution permissions.
2. Checked-in executable implementation and checked-in artefacts under `src/`
   or `workflows/src/`
3. Repo-local skills under `./.agents/skills/`
4. This `AGENTS.md` for shared repo-wide rules
5. `CONVENTIONS.md`
6. `README.md`
7. Other repo docs such as `OVERVIEW.md`

If docs or skills conflict with the checked-in executable implementation or
artefacts, follow the checked-in implementation and raise the drift clearly.
Treat playgrounds, scratch directories, and prose examples as supporting
context only unless they match maintained checked-in patterns.

## Workflow Model

- PolyAPI runtime flow is usually schemas, webhooks, triggers, and functions.
  GraphQL subscriptions, jobs, `vari`, `tabi`, and Canopy artefacts may also
  participate depending on the repo.
- Keep one workflow per `src/<workflow>/` or `workflows/src/<workflow>/`
  folder, depending on the repo layout.
- TypeScript repos commonly keep `artifacts/`, `client/`, `server/`, and
  `types/` together under the workflow.
- Put genuinely shared reusable code under `src/utilities/` or the repo's
  equivalent shared utility area.
- Follow the repo's active function metadata pattern. Some repos use inline
  `polyConfig`; others use checked-in function metadata JSON. Do not mix
  patterns without evidence.

## Artefact Contract

- Keep TypeScript, JSON artefacts, and tests aligned in the same change.
- Use `https://eu1.polyapi.io/swagger-json` as the source of truth for the JSON
  field shape of platform-managed artefacts.
- Use checked-in repo patterns for file placement, naming, and workflow
  structure.
- One public endpoint should map to one explicit webhook artefact.
- Do not loosen schemas or introduce generic catch-all endpoints just to make a
  migration pass.
- Never commit or expose secret values. Record secret names only.

## PolyAPI SDK Rules

- Call generated `poly.*` functions directly through the SDK namespace.
- Call generated `vari.*` paths directly through the SDK namespace.
- Do not use `as unknown as` or local compatibility aliases to reshape
  `poly.*` or `vari.*`.
- If generated SDK types are stale, run the repo's SDK generation command
  instead of casting around the mismatch.
- Prefer generated `schemas.*` and `tabi.*` types when they represent the
  platform contract.
- Keep function metadata aligned with deployed function names, contexts, and
  trigger or subscription wiring.

## Environment and Tooling

- Use the package manager and workspace model already pinned by the target repo.
- Discover build, sync, and test commands from the checked-in `package.json`
  and related tooling before changing them.
- Run the repo's checked-in build, sync, and test path after code or artefact
  changes.
- Do not upgrade `polyapi` or related dependencies casually.

## Task Entry Points

- Use `./.agents/skills/coding-conventions/SKILL.md` before naming functions,
  contexts, files, or workflow folders.
- Use `./.agents/skills/artefacts-usage/SKILL.md` before creating or reviewing
  workflow layout or JSON artefacts.
- Use `./.agents/skills/polyapi-sdk/SKILL.md` before writing, syncing, or
  deploying PolyAPI TypeScript code.
- Use `./.agents/skills/coding-standards/SKILL.md` before writing logging or
  error handling, and when behaviour-changing work requires `OVERVIEW.md`
  updates.
- If installed, use `./.agents/skills/design-analysis/SKILL.md` as soon as a
  target PolyAPI design is provided.
- If installed, use `./.agents/skills/generate-overview/SKILL.md` when
  behaviour-changing work requires creating or refreshing `OVERVIEW.md`.
- Use `README.md` for setup and local tooling.
- Use `CONVENTIONS.md` for the human-readable convention reference.

## Change Workflow

1. Inspect a comparable maintained workflow before inventing new patterns.
2. Edit code, artefacts, and tests together.
3. Run the repo's checked-in build, sync, and test path.
4. Update same-folder `OVERVIEW.md` when behaviour changes.
5. Keep changes small, reviewable, and easy to verify.

## Quality Expectations

- Preserve existing repo behaviour and checked-in patterns unless the user
  explicitly asks to change them.
- Reuse existing shared components before introducing new ones.
- Do not invent new namespaces, webhook shapes, trigger wiring, logger
  patterns, or error envelopes without checking comparable maintained workflows
  first.
- Keep outputs deterministic and boundary behaviour explicit.
- Handle errors explicitly and log without exposing secrets.

## Security Constraints

- Never print, quote, or persist secret values.
- Env files and config files may be inspected only when needed for the task;
  report variable names and non-secret configuration, not secret contents.
- Do not access external secret managers unless the user explicitly asks and
  the active environment permits it.
- Do not execute release, deploy, publish, or remote-changing commands unless
  the user explicitly asks and the target repo rules allow it.
- Treat dry-run, build, type-check, and test commands as validation when the
  target repo documents them as safe.
- Do not commit or push unless the user explicitly asks.
