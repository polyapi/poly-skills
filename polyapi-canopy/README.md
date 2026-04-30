# polyapi-canopy

Canopy-specific guidance for future agents working on Canopy UI and
PolyAPI-backed Canopy features.

## Installed Files

- [AGENTS.md](./AGENTS.md) - repo-wide Canopy agent rules
- [.agents/skills/canopy-core/SKILL.md](./.agents/skills/canopy-core/SKILL.md) -
  architecture, source map, workflow, deployment
- [.agents/skills/canopy-config-ui-runtime/SKILL.md](./.agents/skills/canopy-config-ui-runtime/SKILL.md) -
  collection config, rendering, actions, filters, execution
- [.agents/skills/canopy-security-auth/SKILL.md](./.agents/skills/canopy-security-auth/SKILL.md) -
  auth, access logs, roles, permissions, MFA, API keys

Each skill has a local `references/REFERENCE.md` beside its `SKILL.md` with the
project-specific file map, source-of-truth notes, and common traps.

## Skill Layout

This repo expects skills under `./.agents/skills/`:

```text
AGENTS.md
README.md
.agents/
  skills/
    canopy-core/
      SKILL.md
      references/REFERENCE.md
    canopy-config-ui-runtime/
      SKILL.md
      references/REFERENCE.md
    canopy-security-auth/
      SKILL.md
      references/REFERENCE.md
```

Copy each full skill folder, including its `references/` directory.

## Task Entry Points

- Use `./.agents/skills/canopy-core/SKILL.md` when onboarding, mapping source
  ownership, planning cross-layer Canopy work, or checking PolyUI config
  deployment requirements.
- Use `./.agents/skills/canopy-config-ui-runtime/SKILL.md` before changing
  collection config, filters, fields, actions, generic UI rendering,
  execute-function pages, collection CRUD, or runtime request mapping.
- Use `./.agents/skills/canopy-security-auth/SKILL.md` before changing auth,
  sessions, access logs, roles, permissions, visibility, MFA, API keys, tenant
  isolation, or other security-sensitive UI/runtime behavior.

## Main Themes

- Canopy is a Next.js/React shell rendered from PolyAPI application config.
- Collection work is usually config-first: inspect `collection.json` and
  `api.json` before changing React code.
- Runtime request construction matters as much as config. Optional empty filter
  values must often be omitted, not sent as empty strings.
- Auth, access logs, roles, visibility, tenant boundaries, MFA, and API key
  behavior are security-sensitive.
- Generic collection pages and action bars should stay generic; collection
  behavior belongs in JSON when supported.
- Larger or logic-heavy UI blocks should be extracted into child components as
  render boundaries, with memoization used only when justified.
- Any merged `collection.json` or associated `api.json` change requires the
  manual PolyUI config deployment workflow for `develop`.

## Use With

When available, also install these shared skills into the target repo's
`./.agents/skills/` directory:

- `design-analysis` from `polyapi-common`
- `markdownlint-compliance` from `common`

Those skills provide broader PolyAPI platform and Markdown guidance. This pack
adds Canopy-specific UI, config, auth, deployment, and workflow rules.
