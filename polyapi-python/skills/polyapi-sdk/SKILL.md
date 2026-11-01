---
name: polyapi-sdk
description: Use when configuring the native PolyAPI Python SDK, checking generated types or function deployment, or using Flow resource cleanup and server-function logs.
---

# Skill: PolyAPI SDK

## Purpose

Reference guide for writing correct PolyAPI Python code: setup, type system rules, deployment commands, and known SDK quirks that must be handled to avoid runtime and generation errors.

## When to use

Load this skill before writing any PolyAPI Python code. The rules here are non-obvious and diverge from standard Python conventions in ways that cause silent failures if ignored.
For exception ordering and logging behaviour, also follow `coding-standards`.

---

## Python version

Match the target repo's toolchain. The current GHA target repo uses Python 3.12. Verify with `python --version`.

---

## TypedDict — critical rule

**Always import `TypedDict` from `typing_extensions`, not from `typing`.**

```python
# CORRECT
from typing_extensions import TypedDict, NotRequired, Literal, Any

# WRONG — will cause type inference failures in the PolyAPI SDK
from typing import TypedDict
```

Use Python 3.10+ syntax for all other annotations:

```python
list[str]           # not List[str]
dict[str, Any]      # not Dict[str, Any]
str | None          # not Optional[str]
str | int           # not Union[str, int]
```

---

## Circular import pattern — critical rule

**Never reference `poly.<context>.<Type>` inside a `TypedDict` definition when deploying to the same context.**

The SDK generator creates `__init__.py` files that import all functions. Cross-referencing a type from a sibling function in the same context causes a circular import at SDK load time.

Redeclare the `TypedDict` locally in each file that needs it. Do not import sibling SDK types from the same context.

---

## Webhook-linked SFX contract — critical rule

Any SFX linked to a webhook receives exactly three positional arguments:

| Argument | Type | Contents |
| --- | --- | --- |
| `__event` | `dict` | Request body or event payload |
| `headers` | `dict` | HTTP or trigger headers |
| `params` | `dict` | Query and path parameters |

When a shared HTTP router sits in front of the SFX, `headers` often includes keys such as `X-Http-Method`, `X-Original-Uri`, `Authorization`, and `X-Force-Log`.

---

## SFX function shape

Server functions must always return a `dict`. Follow `coding-standards` for exception ordering and logging, and follow any project-specific standards skill for the boundary payload and status-setting pattern.

---

## Core rules

- Use the active repo's pinned native SDK and environment manager; reuse its
  configured connection instead of reinstalling or upgrading the SDK.
- Regenerate after catalogue changes unless the repo's Flow command already
  does so. Keep generation and deployment on the same target.
- Import `TypedDict` from `typing_extensions`, never from `typing`.
- Use Python 3.10+ type syntax for other annotations.
- The `--context` must match the active repo's naming conventions.
- Webhook-linked SFX handlers take exactly `__event`, `headers`, and `params`.
- Server functions must return a `dict` and handle top-level failures cleanly.
- Use `coding-standards` for exception handling structure, plus any project-specific standards skill for repo-specific boundary behaviour.

## Reference

See `./references/REFERENCE.md` for setup commands, deployment commands, type mapping, circular import examples, webhook-linked SFX conventions, and virtual environment notes.

## Flow Operations

For scoped resource deletion or server-function log retrieval, read
[`references/FLOW.md`](./references/FLOW.md). It covers the current Python
Flow interface, exact/descendant contexts, preview/apply boundaries, deletion
verification and log pagination. Discover the target repo's available commands
before using these template examples.

For OpenAPI/Swagger API Function training, use `api-function-training` when
installed. Its dedicated workflow covers operation selection, saved models,
plain-text descriptions and native SDK verification. A copied SDK skill does
not require installing Flow into a native-CLI project.
