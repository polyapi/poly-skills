# poly-skills

Curated skills and agent packs for MuleSoft-to-PolyAPI migration work, reusable
PolyAPI implementation guidance, and general repo hygiene.

## Browse

- [mulesoft-to-polyapi](./mulesoft-to-polyapi/README.md): MuleSoft analysis and
  migration pack
- [polyapi-common](./polyapi-common/README.md): shared PolyAPI design and repo
  guidance
- [polyapi-python](./polyapi-python/README.md): Python-specific PolyAPI skills
- [polyapi-typescript](./polyapi-typescript/README.md): TypeScript-specific
  PolyAPI skills
- [common](./common/README.md): broad reusable non-PolyAPI skills

## Index

See [CATALOG.md](./CATALOG.md) for the full skill and pack catalog.

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
