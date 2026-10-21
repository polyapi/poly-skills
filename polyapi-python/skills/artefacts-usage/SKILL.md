---
name: artefacts-usage
description: Use when creating or reviewing PolyAPI Python workflow layout, JSON artefacts, portable references, resource ownership, or sync lifecycle changes.
---

# PolyAPI Python artefacts

Start with the target repository's conventions, maintained workflow, and checked-in
validators/deployer. Resource JSON and deployed API payloads can differ: inspect
reference resolution and transformations before treating an example as a contract.

## Placement and contracts

- Use the existing workflow root, such as `src/` or `workflows/src/`. Keep one
  workflow per folder and shared implementations under its `utilities/` area.
- Create only directories the workflow needs. Do not add empty `types/`,
  `deployment/`, or `scripts/` folders. Verify bundling before introducing local
  runtime imports; keep one-off operator scripts outside function discovery.
- Put resources under the supported `artefacts/` categories. Preserve platform
  spellings such as `ai-functions`. Training inputs belong in `specs/` or the
  repository's design-source area; a normal sync need not train them.
- Use checked-in validators for local checks. Refresh them only through the
  repository's supported command when available, using the explicitly selected
  instance's `/swagger-json` or an approved saved contract. If no adapter or
  validator exists, use that platform contract directly; do not invent Flow-only
  fields or require new tooling. Do not assume a region.
- Keep schemas, webhook authentication/security, trigger arguments, function
  contracts, response statuses, and enabled states aligned. Preserve existing
  public endpoint contracts; do not weaken validation or invent a catch-all
  endpoint merely to make a migration pass.

## References, ownership, and lifecycle

- Use the project's declared owned namespaces. Where the deployer supports
  `POLYAPI_NAMESPACE(S)`, keep local contexts within those roots and use owned
  prefixes for context-less resources such as jobs and triggers.
- Prefer portable function/variable context-and-name references when supported.
  Let the target-bound resolver supply IDs; do not paste environment-specific
  IDs into portable examples to bypass resolution.
- Referencing an accessible external function does not make it project-owned.
  Before deletion, prove ownership, exact identity, scope, and dependent links;
  review the deployer's orphan rules and the proposed remote change.
- Never embed credentials in JSON or persist resolved secrets through environment
  substitution. Declare secret Vari metadata and configure values through the
  authorized target workflow. Preserve existing sensitive values during sync.
- Keep jobs and streams at their intended enabled state. Confirm whether updates
  are in-place or destructive. Subscription recreation may reset offsets;
  preserve its separate confirmation. Canopy identity must be explicit—absence
  from a local folder alone does not prove an application is safe to delete.

## Validate

Run the repository's focused preflight/resource tests and normal checks. Preview
only the intended target and scope before an authorized sync; local validation
does not prove remote references exist or grant permission to deploy/delete.
Update the workflow overview when contracts change.

See [the reference](references/REFERENCE.md) for layout, resource mappings, and
field/lifecycle checks. Use `coding-conventions` for naming and `polyapi-sdk` for
single-file Python deployment constraints.
