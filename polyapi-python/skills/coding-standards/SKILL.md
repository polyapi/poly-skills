---
name: coding-standards
description: Use when implementing or reviewing PolyAPI Python error boundaries, logging, redaction, alert delivery, retries, or behavior changes that affect workflow documentation.
---

# PolyAPI Python coding standards

Follow the active repository's contracts and nearest maintained workflow. Keep
response envelopes, logger interfaces, and alert wiring specific to that repo.
Use `polyapi-sdk` for native SDK types, calls, and deployment constraints.

## Errors and response boundaries

- Catch specific expected failures where recovery is possible. Let unexpected
  programming errors propagate to the established boundary; do not hide contract
  mismatches behind guessed field names or successful fallback responses.
- At a public boundary, preserve the established error envelope and HTTP status
  behavior. If HTTP status is separate response metadata, set it explicitly.
- Use bounded safe messages. Exception text, URLs, headers, provider responses,
  and subprocess output can contain credentials or private data.
- Preserve exception causes when safe and useful internally. When translating a
  sensitive upstream failure, do not expose its raw text through chaining,
  logging, alerts, or returned payloads. Use `from None` at that sanitizing edge.
- Await SDK and notification work when their outcome matters. Preserve the
  existing alert contract; best-effort notification failures must not replace
  the original controlled failure. A global error handler must not raise again
  because its notification failed.
- Add retries around side effects only after checking idempotency and the
  upstream retry contract. Preserve existing behavior unless the task changes it.

## Useful, safe logging

Reuse the project's structured logger. Keep INFO to compact milestones,
outcomes, counters, and durations. Use DEBUG for details that explain business
branching and mapping. At ERROR, include useful sanitized request/response
fields, upstream status, operation, and retry decision when available.
Preserve the project's execution/request correlation fields across related logs
and alerts so the operator can follow one invocation.

DEBUG is not permission to expose secrets. Select safe fields before logging;
never log arbitrary exceptions, credential headers, injection references, or raw
URLs. Apply the existing recursive sanitizer to nested dictionaries and lists,
and bound depth, length, and item count. Key redaction alone cannot remove a
credential embedded in free text, so omit or replace unsafe text fields. When no
safe payload subset is known, retain operational metadata only.

Prefer a few useful diagnostic entries to fragmented field noise. Do not erase
safe payload evidence needed to explain a failure, or log full payloads merely
because they are available. Suppress noisy transport loggers where appropriate.

## Tests and maintenance

Test observable boundaries: malformed inputs, exact SDK arguments and await
behavior, upstream failures, HTTP status, and safe failure messages. For logging
or alerts, cover nested sensitive values and delivery failure with synthetic
inputs. Reuse existing test and redaction helpers; avoid a new logging framework.
Local tests should mock network/SDK boundaries; live execution remains opt-in.

Run the repository's focused checks. Refresh the owning workflow or utility's
same-folder `OVERVIEW.md` when runtime behavior changes; discover its root from
project configuration rather than assuming `src/`. Formatting-only changes do
not require a rewrite. Use `generate-overview` when installed, or follow the
repository's maintained overview format.

See [the reference](references/REFERENCE.md) for safe Python examples, log levels,
and boundary checks.
