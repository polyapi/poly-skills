# PolyAPI Python SDK reference

## Setup and target selection

Read the project's manifest, lockfile, README, and deploy tooling first. Use its
pinned Python and native `polyapi-python` versions with its existing package
manager. Do not install the newest SDK or introduce another dependency manager
as an implicit setup step.

The native Python SDK uses `POLY_API_BASE_URL` and `POLY_API_KEY`. Use the
explicitly selected instance and environment; do not assume a region or copy
another project's credentials. Preserve any environment pin and execution-key
requirements imposed by the deployer. Never inspect real environment files or
`polyapi/.config.env` to discover credentials.

When the repository delegates to the native CLI, inspect its installed help:

```bash
python -m polyapi --help
python -m polyapi function add --help
```

Run these through the project's interpreter, such as `uv run --locked python`
when that is its documented workflow. Setup and generation require the selected
target; they are not offline verification commands. For authorized generation,
the native command is:

```bash
python -m polyapi generate
```

Prefer the repository's target-bound Flow/deploy command when present. It may
also enforce ownership and production checks and regenerate the SDK. Do not
bypass those controls by switching to a bare native deployment command.

For a project that already uses the native CLI, the deployment form is:

```bash
python -m polyapi function add get_tags ./server/get_tags_sfx.py --context example.tags --server
```

This is a remote write, not a validation command. Substitute the actual
entrypoint, file, and authorized context; use `--client` instead for a client
function. Verify these arguments with the pinned CLI's help. Native `function
add` in `0.3.20.dev4` regenerates by default unless `--skip-generate` is used;
do not add an unnecessary second generation step.

## Types and source packaging

| Schema or return type | Python annotation |
| --- | --- |
| `integer` | `int` |
| `number` | `float` |
| `string` | `str` |
| `boolean` | `bool` |
| `array` | `List[ItemType]` from `typing`, or `list[ItemType]` when parser support is verified |
| `object` | a local `TypedDict` or the supported dictionary contract |
| `void` (SDK no-return type) | Verify parser support; a Python `None` annotation alone may not emit `void` |

Use annotations supported by the pinned Python/SDK pair. Import `TypedDict`
from `typing_extensions`; do not substitute `typing.TypedDict` without verifying
that the pinned SDK parser supports it. Recheck parser behavior during upgrades.

Python syntax validation alone does not prove the deployed type contract. In
`polyapi-python 0.3.20.dev4`, the top-level signature parser reads `list[str]`,
`dict[str, str]`, `str | None`, and a `None` return as `Any`; it recognizes
`List[str]`, `Dict[str, str]`, and named local types. Inspect emitted argument
and return types and schemas for every boundary shape, including optional and
no-return types.
This limitation concerns function signatures; fields inside `TypedDict` use a
different schema path. Do not rewrite all internal Python annotations.

For single-file deployment, define required types in the submitted file. This
example uses the supported array annotation at the function boundary:

```python
from typing import List
from typing_extensions import TypedDict


class RequestPayload(TypedDict):
    tags: List[str]


def get_tags(payload: RequestPayload) -> List[str]:
    return payload["tags"]
```

Do not import a neighboring `_types.py` unless the actual deployer packages it.
Do not reference a sibling generated type in a `TypedDict` definition during
same-context generation: eager generated imports can create a circular import.

Inspect the SDK parser's dependency discovery and the deployer's submitted
source/requirements when diagnosing import failures. A local virtual environment
and a deployed function are different environments. Declare and install actual
runtime dependencies; do not suppress missing-package errors, substitute empty
modules, or patch SDK package lookup to make parsing succeed.

## Function and generated-call contracts

A webhook trigger commonly maps event, headers, and params to a server function.
Verify its actual mapping, security-function contract, and optional router
headers. Other server functions can take different arguments and return scalar,
Boolean, or structured results supported by their generated contract.

| Generated surface | What to verify |
| --- | --- |
| API/server function | Actual `_async` callable, arguments, and return envelope |
| Async client function | Declared name and whether the caller must await it |
| HTTP handler | Input mapping, response payload, and response-status metadata |
| Webhook security function | Expected acceptance/rejection result, including `bool` |

Inspect source without executing or printing credential configuration. Use exact
API field names and generated SDK identifiers, even when they use different casing
from locally authored Python files.

## Vari and injection

Read by exact context path. If the generated `get_async()` returns JSON text,
use `json.loads`, check the resulting type and required fields, and surface a
bounded configuration error. Do not decode an already structured result blindly.

SECRET injection is an opaque reference passed directly into a generated
API/server call that supports it. The consumer must not resolve or serialize the
reference itself. Test that the exact reference reaches the boundary unchanged.
That local test does not prove the target resolves it. Direct-execute transport
requires explicit support; reject it for an injection path when unsupported.

Keep OBSCURED, PARTIAL, and SECRET values uncached. Cache NONE settings only with
an explicit lifetime appropriate to their freshness needs.

## Verification boundaries

- Local parser/tests: imports, annotations, payload shapes, awaits, error branches.
- Target generation: actual environment catalog and generated signatures.
- Deployed execution: function build, routing, permissions, and secret resolution.

Report each separately. Preserve the user's commit, deployment, and publication
boundaries; passing tests do not authorize those effects.
