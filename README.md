# poly-skills

Curated skills and agents for PolyAPI project implementations. It covers a wide range of use cases, including coding PolyAPI projects in TypeScript or Python and migrating from MuleSoft to PolyAPI.

## Browse

- [boomi-to-polyapi](./boomi-to-polyapi/README.md): Dell Boomi analysis and
  migration pack
- [mulesoft-to-polyapi](./mulesoft-to-polyapi/README.md): MuleSoft analysis and
  migration pack
- [polyapi-common](./polyapi-common/README.md): shared PolyAPI design and repo
  guidance
- [polyapi-python](./polyapi-python/README.md): Python-specific PolyAPI skills
- [polyapi-typescript](./polyapi-typescript/README.md): TypeScript-specific
  PolyAPI skills
- [common](./general/README.md): broad reusable non-PolyAPI skills

## Index

See [CATALOG.md](./CATALOG.md) for the full skill and pack catalog.

API Function training has dedicated skills for
[Python](./polyapi-python/skills/api-function-training/SKILL.md) and
[TypeScript](./polyapi-typescript/skills/api-function-training/SKILL.md).
Each language pack's `polyapi-sdk` skill includes Flow resource cleanup and
server-function log retrieval guidance.

## Using In Projects

To use a skill in another repo, copy the full relevant skill folder into that
repo's `.agents/skills/` directory.

- Copy the whole folder, not just `SKILL.md`.
- Keep supporting files such as `references/`, `scripts/`, and templates with
  the skill.
- Preserve the folder name so the skill name and folder name still match.
- Skill folders belong under `.agents/skills/`.
- Repo-level `AGENTS.md` files belong at the root of the target repo, not
  under `.agents/`.
- If you are using a language pack, use that pack's `AGENTS.md` as the starting
  point for the target repo's root `AGENTS.md`.
- In the target repo's root `AGENTS.md` or agent instructions, tell agents to
  load the copied skill when relevant.
- If you copy an agent playbook or pack-level workflow, also copy the skills it
  depends on or update the referenced paths.

### Agent File Conventions

- Pack-level `AGENTS.md` files are repo-entrypoint templates.
- If you copy `polyapi-python/AGENTS.md`, `polyapi-typescript/AGENTS.md`, or a
  similar pack-level guide, it should become the target repo's root
  `AGENTS.md`.
- `specialised_agents/*.md` files are task-specific playbooks, not the default
  repo entrypoint.
- If you copy a specialised playbook, place it in a normal repo folder such as
  `<target-repo>/agents/` or `<target-repo>/specialised_agents/`, then have the
  root `AGENTS.md` tell agents when to use it.
- Never put repo-entrypoint `AGENTS.md` files or specialised playbooks under
  `.agents/skills/`. That area is only for skills.

Example:

```text
poly-skills/polyapi-python/AGENTS.md
  -> <target-repo>/AGENTS.md

poly-skills/polyapi-python/skills/coding-conventions/
  -> <target-repo>/.agents/skills/coding-conventions/

poly-skills/mulesoft-to-polyapi/specialised_agents/POLYAPI_CODEAGENT.md
  -> <target-repo>/agents/POLYAPI_CODEAGENT.md
```

## TODO

Missing skills. Volunteers welcome.

These are the highest-signal gaps based on real production PolyAPI workflow
repos, especially for bringing `polyapi-python` closer to the day-to-day
patterns used in production.

- `canopy-ui-creation`: guidance for creating and maintaining Canopy UI flows
  and related artefacts

Baseline construct definitions live under `polyapi-common/skills/polyapi-constructs/`.
AI Function selection and Flow artefact guidance lives under
`polyapi-common/skills/ai-functions/`.
Tabi implementation guidance now lives under `polyapi-common/skills/tabi/`.

- `vari-and-tabi-patterns`: when to model data in vari vs tabi, how to handle
  secrets vs config vs cache, and how jobs fit around retention and cleanup

If you want to pick one up, create a branch named after the skill or change and
open a PR to another member of the team for review.

## Contributing

Use a short-lived branch for every repo change.

1. Create a branch named after the skill or the specific change being made.
   Examples:
   - `writing-skills-update`
   - `design-analysis-clarifications`
   - `generate-schemas-doc-fix`
2. Make the change in the relevant pack or skill folder.
3. Open a pull request for review by another member of the team.
4. Merge only after that review is complete.

When possible, keep each branch focused on one skill or one tightly related
change so the review stays easy to follow.

## Maintainer Guidance

When creating, editing, moving, or reviewing skills in this repo, agents should
follow [.agents/skills/writing-skills/SKILL.md](./.agents/skills/writing-skills/SKILL.md).

That `.agents/skills` area is repo-maintenance guidance, not part of the public
skill catalog intended for cherry-picking into other projects.
