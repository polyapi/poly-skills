# PolyAPI Python coding standards reference

## Catch, translate, and preserve the boundary

| Situation | Action |
| --- | --- |
| Expected failure with a valid recovery | Catch the specific exception and follow the established recovery contract |
| Caller can handle the failure | Let it propagate, or add safe context |
| Sensitive upstream error crossing a boundary | Translate to a fixed safe error and suppress the unsafe cause |
| Unexpected helper or client error | Let the established top-level boundary handle it |
| Public boundary handles an error | Log safe diagnostics and preserve the repository's payload and status contract |
| Cleanup regardless of outcome | Use a context manager or `finally` |

Do not universally return dictionaries: security functions, event handlers, and
ordinary functions can have different contracts. A returned status field does
not substitute for the runtime's HTTP response metadata.

### JSON validation

```python
import json


def decode_config(raw: str) -> dict:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("Configuration must contain valid JSON") from None
    if not isinstance(value, dict):
        raise ValueError("Configuration must be a JSON object")
    return value
```

Validate required fields against the actual schema after decoding. Do not log
`raw` or echo the parser error. The caller must decide how this failure maps to
its response, status, and alert contract.

### HTTP and network errors

```python
import urllib.error
import urllib.request


def read_response(request: urllib.request.Request) -> bytes:
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Upstream request failed with HTTP {error.code}") from None
    except urllib.error.URLError:
        raise RuntimeError("Upstream request could not be completed") from None
    except OSError:
        raise RuntimeError("Upstream response could not be read") from None
```

This illustrates exception translation, not a replacement for generated SDK
calls. Adapt exception types to the installed SDK and HTTP library. Do not
include URL, reason, headers, or arbitrary response text in the replacement
error. The existing logger may receive approved status/operation fields.

Use `raise ... from error` where the cause is known to be safe and aids diagnosis.
Suppressing a cause does not sanitize a separate raw log or alert call.

### Subprocess and resource failures

Catch `subprocess.TimeoutExpired`, `subprocess.CalledProcessError`, `OSError`, or
the library's specific database exception when appropriate. Log safe timeout,
exit-code, or operation fields. Commands, stdout, stderr, file paths, and database
exception messages may contain credentials or private data; do not forward them
unchanged. Keep cleanup failures from replacing the primary failure unless the
established integrity contract requires them to propagate.

## Logging levels and content

| Content | Level |
| --- | --- |
| Started, finished, skipped, or posted outcome | INFO |
| Final counters and elapsed duration | INFO |
| Sanitized business inputs, outputs, mapping, and decision details | DEBUG |
| Retryable failure with the approved retry decision | WARN |
| Terminal failure with safe operation/status and useful sanitized payload details | ERROR |
| Routine transport chatter | Suppress |

INFO is the operator timeline. Avoid request/response bodies, headers, full
URLs, and transport internals there. DEBUG and ERROR should still contain useful
business evidence when it is safe: selected records, relevant rules, response
status, or approved request/response fields. Do not turn useful diagnostics into
only booleans when a safe compact payload explains the failure.

Select an allowed subset using known SDK/schema fields. Then use the project's
sanitizer recursively for dictionaries and lists and cap size/depth before
sending to the log sink. Credential keys can vary in case and spelling;
sanitization must cover the actual contract. A token embedded in `message`, a
URL, or exception text survives key-based redaction: replace or omit that field.
Never assume arbitrary payloads become safe simply by naming them `sanitized`.

For a logger with a message/context-dictionary interface, safe metadata examples
are:

```python
call_logger["info"]("Workflow finished", {"outcome": "success", "count": 3})
call_logger["warn"]("Retry scheduled", {"operation": "fetch_advice", "attempt": 2})
call_logger["error"]("Upstream request failed", {"operation": "fetch_advice", "status": 503})
```

Use the actual project's interface and verified fields. Add safe payload subsets
when they materially explain the error; do not copy raw exceptions or URLs.

## Notification containment

Preserve whether the existing alert is required or best-effort. For best-effort
alerts, use a fixed safe alert payload and isolate notification failures:

```python
async def notify_failure(notify, call_logger) -> None:
    try:
        await notify({"message": "Workflow failed", "operation": "process_event"})
    except Exception:
        call_logger["error"]("Failure notification could not be delivered", {})
```

Use the real generated notification signature, not this illustrative callable,
and ensure the logger itself is safe/non-throwing or handled at that boundary.
This broad catch belongs around the secondary best-effort effect, not around all
business logic. A global error handler must preserve its controlled result even
when notification delivery fails. Do not launch an unawaited alert task.

## Review checklist

- Exact data shapes and SDK calls; no guessed alternate field names.
- Specific handled failures and the correct public payload/status contract.
- Useful diagnostics without credentials in nested data, text, URLs, or causes.
- Best-effort alert failure does not replace the original error result.
- No retry of side effects without an idempotency/retry contract.
- Focused tests cover the changed observable behavior with synthetic data.
- The owning workflow or utility overview matches changed runtime behavior.
- Verification states distinguish local tests from actual deployed evidence.
