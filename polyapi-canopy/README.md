# polyapi-canopy

Guidance for agents and customers who are building a Canopy application
through an Application JSON.

This pack is for authoring, reviewing, and debugging customer-facing Canopy
apps: collections, forms, actions, argument mapping, login/sign-up flows,
variables, and deployment to a Poly tenant. It is not a guide for developing
the Canopy runtime itself. It is not a PolyAPI workflow template pack.

If you are working in a PolyAPI workflow repo (the `workflows/src/<workflow>/`
layout), Canopy UI artefacts belong under
`workflows/src/<workflowName-or-utilities>/artefacts/canopy/`.

## What This Pack Is For

Use this pack when you need to:

- design a new Canopy app for a customer
- extend an existing Canopy app by editing its Application JSON
- debug why a collection, form, or action is not behaving as expected
- verify that Application JSON matches real Canopy runtime behavior
- guide a customer through deployment in PolyUI

## Installed Files

- [AGENTS.md](./AGENTS.md) - high-level rules for agents working on Canopy app authoring tasks
- [skills/canopy-ui/SKILL.md](./skills/canopy-ui/SKILL.md) - the main customer-facing authoring guide for Application JSON

## Skill Layout

When installed into a target Canopy UI repository, copy the skill folder into
`./.agents/skills/`:

```text
AGENTS.md
README.md
.agents/
  skills/
    canopy-ui/
      SKILL.md
```

Copy the full `canopy-ui` skill folder.

## Where To Start

For almost all tasks, start with [skills/canopy-ui/SKILL.md](./skills/canopy-ui/SKILL.md).

That skill covers the main authoring surface:

- app structure and navigation
- collections, item pages, and standalone forms
- prepare and submit lifecycle
- argument mapping to PolyAPI functions
- filters driven by `queryParam`
- response config, redirect behavior, and templating
- variables, secrecy, MFA, and PolyUI deployment

## Recommended Workflow

When helping a customer or authoring an app yourself, use this order:

1. Confirm the business flow the app needs to support.
2. Confirm which Poly resources already exist in the tenant: functions,
   variables, identity providers, tables, schemas, webhooks.
3. Shape the Application JSON around the user journey: collections, forms,
   actions, and routes.
4. Validate that each function call has the right argument mapping.
5. Check whether query params, defaults, redirects, and response views match
   the intended UX.
6. Deploy through PolyUI, unless the project explicitly uses a checked-in app
   config plus a documented deployment workflow.

## What Matters Most

- Canopy is config-driven. Most customer app work should happen in the
  Application JSON, not by changing the runtime.
- The most common source of mistakes is not layout but data flow: wrong
  function paths, wrong argument names, wrong query param keys, or wrong
  response shape.
- Security-sensitive behavior still matters in customer apps: API keys,
  MFA-protected actions, tenant scoping, role-gated fields, and secret-backed
  variables should be treated carefully.
- Customers usually deploy via PolyUI. Workflow-based deployment can exist in a
  repo, but it should be treated as project-specific, not as the default.

## Keep It Customer-Facing

Prefer guidance that helps a customer or agent ship a working app:

- explain what JSON to write
- explain what runtime behavior to expect
- explain what must already exist in PolyUI
- explain how to validate and deploy the app

Avoid adding details that are mainly about Canopy internals unless they are
needed to explain observable app behavior.

## Use With

When available, these related skills are useful alongside this pack:

- `design-analysis` from `polyapi-common` for turning business requirements
  into a concrete Canopy app structure
- `markdownlint-compliance` from `common` when editing Markdown docs
