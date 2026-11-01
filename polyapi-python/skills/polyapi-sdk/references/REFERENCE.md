# polyapi-sdk Reference

## Setup commands

Use the target repo's pinned SDK, environment manager and existing connection.
The commands below are native SDK entry points, not instructions to reinstall
or upgrade an already configured project. Use the repo's `uv`, `venv`, or other
documented runner; Flow may already perform SDK regeneration after deployment.

```bash
python -m polyapi setup
python -m polyapi generate
```

After catalogue changes, regenerate on the same target if the deployment
command has not already done so.

## Python version

Match the target repo's toolchain. The current GHA target repo uses Python 3.12.

## Type mapping reference

| JSON Schema type | Python type |
| --- | --- |
| `integer` | `int` |
| `number` | `float` |
| `string` | `str` |
| `boolean` | `bool` |
| `array` | `list` |
| `object` | `dict` |
| `void` | `None` |

## Deployment commands

```bash
python -m polyapi function add <function_name> <file>.py --context <context.name> --server
python -m polyapi function add <function_name> <file>.py --context <context.name> --client
```

## Webhook-linked SFX contract

Any webhook-linked SFX receives exactly:

| Argument | Type | Notes |
| --- | --- | --- |
| `__event` | `dict` | Request body or event payload |
| `headers` | `dict` | HTTP or trigger headers |
| `params` | `dict` | Query and path parameters |

In router-driven HTTP flows, `headers` often includes `X-Http-Method`, `X-Original-Uri`, `Authorization`, and `X-Force-Log`.

## Circular import pattern

Never reference `poly.<context>.<Type>` inside a `TypedDict` definition when deploying to the same context.

**Symptom:**

```text
AttributeError: partially initialized module 'polyapi.poly' has no attribute 'utils'
(most likely due to a circular import)
```

**Fix:** redeclare the `TypedDict` locally in each file that needs it.

```python
class PlatformLoggingConfig(TypedDict):
    site: str
    api_key: str

class InitLoggerParams(TypedDict):
    platform_config: PlatformLoggingConfig
```

After fixing, regenerate:

```bash
python -m polyapi generate
```

## SFX function shape

Server functions must always return a `dict`. Use `coding-standards` for exception ordering and logging, and do not let an unhandled exception escape the top-level handler.

```python
async def my_function_sfx(__event: dict, headers: dict, params: dict) -> dict:
    if "required_param" not in params:
        return {"error": "missing required_param"}  # Adapt to the repo boundary contract
    return {"ok": True}
```

Use the active repo's standards skill for project-specific logger wiring and boundary payload rules.

## Virtual environment

```bash
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\activate.bat
source .venv/bin/activate
pip install -e ".[dev]"
```
