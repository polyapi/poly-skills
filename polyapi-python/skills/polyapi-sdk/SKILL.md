---
name: polyapi-sdk
description: Use when implementing or reviewing PolyAPI Python functions, generated SDK calls, runtime types, Vari access, or deployment parsing failures.
---

# PolyAPI Python SDK

Match the target project's pinned Python and `polyapi-python` versions and its
existing install, generate, and deploy commands. Verify contracts against that
SDK's source and generated callables, excluding credential stores. Do not infer
Python behavior from another SDK or upgrade dependencies to hide a mismatch.

## Function source and types

- Use `TypedDict` from `typing_extensions`. Keep structured types local when
  sibling generated types would introduce a circular import.
- For Flow repos using inline metadata, declare a literal `polyConfig` typed as
  `PolyClientFunction` or `PolyServerFunction` from `polyapi.typedefs`. Match its
  name to the actual entrypoint and its context to the project's owned namespace.
- Verify what the deployer uploads. Single-source-file deployment does not
  package neighboring modules. Keep required types/helpers inline or call shared
  deployed functions through the generated SDK; do not import their local files.
- Install runtime dependencies using the project's dependency workflow. Preserve
  native SDK dependency discovery; missing third-party imports or package metadata
  must fail preflight. Generated-namespace parsing support is not a license to
  stub runtime dependencies or invent SDK exports.
- Match arguments and return types to the actual function and trigger contract.
  An event handler may accept event, headers, and params; a security function can
  return `bool`. Server functions do not universally take three arguments or
  return `dict`.

## Generated calls and Vari

- Inspect the exact generated signature and a maintained caller. Generated
  API/server async calls commonly use `_async`; async client functions retain
  their declared names. Await the callable the installed SDK actually exposes.
- Preserve upstream identifiers and response field casing. Validate required
  nested shapes rather than guessing alternative keys.
- Fetch Vari by its exact generated context path. Decode JSON text only when
  the generated return contract requires it, then validate the decoded shape.
- Pass SECRET `.inject(...)` references unchanged to a supported generated
  API/server boundary. Do not read, stringify, cache, or relay them through
  another client function. Verify execution-mode support: direct API execution
  must not be assumed to resolve injected references.
- Do not cache OBSCURED, PARTIAL, or SECRET values. A bounded cache of NONE
  configuration is appropriate only when its freshness requirements permit it.
- For handled HTTP responses, preserve the repository's status-setting pattern.
  `polyCustom.responseStatusCode` controls response metadata; a `statusCode` field
  in a returned dictionary is a separate payload contract.

## Verify and deploy

Use focused local tests for SDK arguments, awaited calls, response validation,
Boolean security decisions, and opaque injection-reference identity. Run the
project's checked-in checks. These do not prove live secret resolution or builds.

Deploy only within the authorized target and scope, using the existing preview
and identity, namespace, execution-key, OTP, and production safeguards. Regenerate
against that same target when the deployed catalog changes; verify whether the
repository's deploy command already does this. Keep live verification explicit.

See [the reference](references/REFERENCE.md) for type mapping, packaging, SDK
inspection, and command selection. Use `coding-standards` for error boundaries.
