# coding-standards Reference

## Overview maintenance

- Every workflow folder under `src/<workflow_name>/` should have an
  up-to-date `OVERVIEW.md`.
- Every utility folder under `src/utilities/<utility_name>/` should have an
  up-to-date `OVERVIEW.md`.
- When runtime behavior changes, refresh the overview in that same folder
  before considering the task complete.
- For new workflow or utility folders, create `OVERVIEW.md` as part of the
  implementation work.
- Formatting-only, comment-only, and non-runtime tooling changes can skip an
  overview refresh.
- Use the `generate-overview` skill to create or refresh the overview so the
  file stays consistent with that skill's local reference.

## Error handling examples

### Catch the most specific exception type

```python
try:
    data = json.loads(raw)
except json.JSONDecodeError as error:
    call_logger["error"]("Invalid JSON", {"error": str(error)})
    return {"error": f"invalid JSON: {error}"}  # Adapt to the repo boundary contract

try:
    data = json.loads(raw)
except Exception as error:
    call_logger["error"]("Unexpected parsing failure", {"error": str(error)})
    return {"error": "something went wrong"}  # Adapt to the repo boundary contract
```

### When to catch vs when to raise

| Situation | Action |
| --- | --- |
| You can recover or provide a fallback | Catch, handle, return a repo-appropriate error payload |
| You cannot recover but the caller can | Catch, add context, re-raise with `from` chaining |
| Unexpected or programming error in helpers or client functions | Let it propagate |
| Unexpected or programming error at the top-level boundary | Log it and return the repo's established error result |
| Cleanup needed regardless of outcome | Use `finally` or `with` |

### Chain exceptions when re-raising

```python
try:
    data = fetch()
except urllib.error.URLError as error:
    raise RuntimeError("failed to fetch config") from error
```

Use `raise ... from None` only when the original exception contains secrets or tokens.

### Boundary return shape is repo-specific

- Use the nearest sibling workflow or utility as the source of truth for the returned payload shape.
- Some repos use simple HTTP payloads such as `{"message": "Bad request"}`.
- Others use richer envelopes such as `{"status_code": 500, "success": False, "error": {"message": "..."}}`.
- Pick one only if it matches the local pattern. Do not normalize the whole repo to a new envelope.

Always log before returning an error result.
This includes unexpected failures at the top-level boundary.

### Order except clauses from most specific to least specific

```python
try:
    conn = oracledb.connect(...)
except oracledb.DatabaseError as error:
    call_logger["error"]("DB connection failed", {"error": str(error)})
    return {"error": f"DB connection failed: {error}"}  # Adapt to the repo boundary contract
except OSError as error:
    call_logger["error"]("OS error", {"error": str(error)})
    return {"error": f"OS error: {error}"}  # Adapt to the repo boundary contract
except Exception as error:
    call_logger["error"]("Unexpected failure", {"error": str(error)})
    return {"error": "Unexpected failure"}  # Adapt to the repo boundary contract
```

### Subprocess error handling

```python
try:
    proc = subprocess.run([...], timeout=60, capture_output=True, text=True)
except subprocess.TimeoutExpired as error:
    call_logger["error"]("Subprocess timed out", {"timeout": error.timeout})
    return {"error": f"subprocess timed out after {error.timeout}s"}  # Adapt to the repo boundary contract
except Exception as error:
    call_logger["error"]("Subprocess failed", {"error": str(error)})
    return {"error": str(error)}  # Adapt to the repo boundary contract

if proc.returncode == 0 and proc.stdout.strip():
    try:
        result = json.loads(proc.stdout.strip())
    except json.JSONDecodeError as error:
        call_logger["error"]("Subprocess returned invalid JSON", {"error": str(error)})
        return {"error": f"subprocess returned invalid JSON: {error}"}  # Adapt to the repo boundary contract
```

### Network calls

```python
try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
except urllib.error.HTTPError as error:
    raise RuntimeError(f"HTTP {error.code} from {url}: {error.reason}") from error
except urllib.error.URLError as error:
    raise RuntimeError(f"Network error: {error.reason}") from error
except OSError as error:
    raise RuntimeError(f"IO error: {error}") from error
```

### Resource cleanup

```python
try:
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(dest)
except zipfile.BadZipFile as error:
    raise RuntimeError(f"archive corrupt: {error}") from error
finally:
    try:
        os.remove(zip_path)
    except OSError:
        pass
```

### Quick reference

| Scenario | Exception type |
| --- | --- |
| Network download | `HTTPError` -> `URLError` -> `OSError` |
| JSON parsing | `json.JSONDecodeError` |
| File or OS operations | `OSError` |
| Subprocess timeout | `subprocess.TimeoutExpired` |
| DB operations | library-specific |
| Missing dict key | `KeyError` |

## Logging

### Log level rules

| What | When | Level |
| --- | --- | --- |
| Input payloads | Complex payloads or branching behaviour | DEBUG |
| Response payloads | Outcome requires body detail | DEBUG |
| Success outcomes | State-changing calls need completion evidence | INFO |
| Error outcomes | Any failed operation or unexpected condition | ERROR |
| Retries | Transient failure triggers a retry | WARN |
| Mapping and decision logic | Conditional logic affects mapping | DEBUG |
| Performance and timing | Integration latency measurement | INFO |
| Final workflow outcome | Completion of integration workflow | INFO |

### Log format

```python
call_logger["debug"]("Input payload", {"payload": payload})
call_logger["info"]("Member balance retrieved", {"member_id": member_id, "status": 200})
call_logger["warn"]("Retry attempt", {"attempt": 2, "reason": str(error)})
call_logger["error"]("Downstream call failed", {"error": str(error), "url": url})
```

### Logging rules

- Always log before returning an error result.
- Do not log secrets, tokens, or passwords at any level.
- Use DEBUG payload logging only when the integration has materially complex conditional behaviour.
- If the repo uses alerting on fatal boundary paths, preserve that alert call before returning.
