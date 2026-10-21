# polyapi-python

Python-specific PolyAPI implementation guidance.

## Repo Entry Point

- [AGENTS.md](./AGENTS.md): generalized repo-wide Python PolyAPI agent guide
  intended to be copied to the root of a target Python repo

## Skills

- [polyapi-sdk](./skills/polyapi-sdk/SKILL.md)
- [coding-conventions](./skills/coding-conventions/SKILL.md)
- [artefacts-usage](./skills/artefacts-usage/SKILL.md)
- [coding-standards](./skills/coding-standards/SKILL.md)

## Using the skills in a project

Copy each selected skill's entire folder, including `references/`, into
`.agents/skills/` using its existing name. For workflow documentation, also copy
[generate-overview](../polyapi-common/skills/generate-overview/SKILL.md) from the
common pack. The naming skill is `coding-conventions`.

Keep Python/SDK pins, workflow roots, commands, and deployment safeguards in the
target project's instructions and conventions. The skills teach reusable SDK,
artefact, naming, logging, and documentation contracts without selecting a
customer or instance. Review shared updates before refreshing project copies.
