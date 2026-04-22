# AGENTS.md

This file applies to work done in this repository.

## Skill Authoring Rule

When creating, editing, reorganizing, or reviewing skills in this repo, load
and follow:

- `.agents/skills/writing-skills/SKILL.md`

Treat that skill as the repo's internal skill-authoring guidance. It is part of
how this repo is maintained, not a public pack intended for normal
cherry-picking.

## Repo Maintenance Rules

- Keep every skill folder self-contained with a `SKILL.md` and any required
  local references or scripts.
- Keep the frontmatter `name` aligned with the skill folder name.
- Preserve the distinction between pack entrypoints and task-specific
  playbooks:
  - `<pack>/AGENTS.md` is the pack's repo-level entrypoint template
  - `<pack>/specialised_agents/*.md` are task-specific playbooks
  - `.agents/skills/` is for skills only
- Update [README.md](./README.md), [CATALOG.md](./CATALOG.md), and any relevant
  section `README.md` files when adding, removing, renaming, or moving skills.
- Prefer local references over links to missing or out-of-repo source files.
- Keep the public taxonomy stable and easy to browse on GitHub.
