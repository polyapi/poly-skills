# AGENTS Guide for PolyAPI Python

Resolve the workflow root from the active repo first. In the rules and examples
below, substitute that root for `src/` (for example, `workflows/src/`).

Shared repo-wide rules for agents working inside a PolyAPI Python repository.
Keep this file focused on source-of-truth order, workflow model, and skill
entry points. Detailed implementation guidance belongs in the local skills.

## Scope

- Applies to all work started from a PolyAPI Python repo.
- Covers shared source-of-truth order, workflow model, repo-wide principles,
  and skill entry points.
- Does not duplicate detailed SDK, naming, artefact, or project-specific
  implementation rules.

## Source of Truth

1. This `AGENTS.md` for shared repo-wide rules
2. Checked-in executable implementation and checked-in artefacts under `src/`
3. Relevant local skills under `./.agents/skills/`
4. `CONVENTIONS.md`
5. `README.md`
6. Other repo docs such as `OVERVIEW.md`

If docs or skills conflict with the checked-in executable implementation or
artefacts, follow the checked-in implementation and raise the drift clearly.
Treat playgrounds, scratch directories, and prose examples as supporting
context only unless they match maintained checked-in patterns.

## Workflow Model

- PolyAPI runtime flow is: schemas -> webhooks -> triggers -> functions.
- Keep one workflow per `src/<workflow>/` folder.
- Python repos commonly keep `server/`, `client/`, `types/`, `tests/`,
  `artefacts/`, `deployment/`, and `scripts/` together under the workflow.
- Put genuinely shared reusable code under `src/utilities/`.
- Keep workflow-local helper scripts local to the workflow or utility they
  support. Create only needed folders; a single-file deployer requires runtime
  types/helpers inline unless it explicitly bundles neighboring modules.

## Artefact Contract

- Keep Python code, JSON artefacts, and tests aligned in the same change.
- Use the selected instance's `/swagger-json` or its saved contract for JSON
  field shapes; also check the repo's local adapter/validators when present.
- Use checked-in repo patterns for file placement, naming, and workflow
  structure.
- One public endpoint should map to one explicit webhook artefact.
- Do not loosen schemas or introduce generic catch-all endpoints just to make a
  migration pass.
- Never commit or expose secret values. Record secret names only.

## Environment and Tooling

- Match the Python version and toolchain already pinned by the target repo.
- Use the repo's existing environment and package-management pattern
  (`venv`, `uv`, `pip`, `poetry`, or equivalent). Do not invent a new one.
- Run the repo's checked-in local tests after code or artefact changes.
  Use its generate/deploy path only for the authorized target and scope.
- Do not upgrade `polyapi-python` or related dependencies casually.

## Task Entry Points

- Use `./.agents/skills/coding-conventions/SKILL.md` before naming functions,
  contexts, files, or workflow folders.
- Use `./.agents/skills/artefacts-usage/SKILL.md` before creating or reviewing
  workflow layout or JSON artefacts.
- Use `./.agents/skills/polyapi-sdk/SKILL.md` before writing or deploying
  PolyAPI Python code.
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
3. Run local tests; use the repo's generate/deploy path when authorized.
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

- Never read or access `.env`, `.env.*`, or any file containing secrets or credentials
- Never access files with extensions like `.key`, `.pem`, `.p12`, `.pfx`, `.crt`
- Only operate within explicitly allowed project directories (e.g. `/src`, `/tests`)
- Do not execute arbitrary shell commands, only use an approved allowlist if provided
- No outbound network calls unless explicitly approved
- Do not access external secret managers (e.g. 1Password, AWS, GCP)
- Never send secrets or sensitive data to the LLM under any circumstance
- Require human approval before modifying CI/CD, dependencies, or reading config files
- Do not persist or store any sensitive data beyond the current session
