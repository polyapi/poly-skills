---
name: coding-standards
description: Use when writing or reviewing TypeScript and the task needs stable standards for readable, strongly typed, contract-driven code, logging, or error handling. In PolyAPI repos, pair this with coding-conventions for platform-specific rules.
risk: unknown
source: community
date_added: "2026-02-27"
---

# Best Practices

Principle-level TypeScript standards for maintainable code.

If the codebase is PolyAPI-based, use
[`coding-conventions`](../coding-conventions/SKILL.md) alongside this skill and
follow its [`CONVENTIONS.md`](../coding-conventions/CONVENTIONS.md) reference for
platform-specific rules around `poly.*`, `vari.*`, `schemas.*`, and artifact
alignment.

## Code Quality Principles

### 1. Readability First
- Keep the main execution path easy to read top-to-bottom
- Prefer descriptive domain names over abbreviations
- Use comments for intent, constraints, or tradeoffs, not narration
- Make the happy path obvious

### 2. Strong Types, Simple Shapes
- Prefer precise types over permissive ones
- Model untrusted input as `unknown`, then narrow deliberately
- Use explicit return types on exported functions when it improves clarity
- Avoid `any` unless it is contained at a compatibility boundary

### 3. Fail Fast at Boundaries
- Validate external input early
- Reject invalid state with actionable errors
- Keep boundary handling close to the entry point
- Prefer guard clauses over deep nesting

### 4. Contracts Drive Code
- Let schemas, interfaces, and tests shape implementation
- Keep outputs deterministic
- Change contracts intentionally, not accidentally
- Version breaking changes instead of smuggling them through

### 5. Simple Beats Clever
- Extract helpers only when they remove real duplication
- Avoid speculative abstraction
- Optimise after evidence, not by instinct
- Prefer explicit control flow over indirection

## TypeScript Standards

### Variable Naming

```typescript
// ✅ GOOD: Domain-specific, intention-revealing names
const paymentContextId = rawMetadata.paymentContextId;
const shouldSkipProfileSync = mapping.skipProfile === true;
const resolvedInstanceConfig = resolveInstanceConfig(config, mapping);

// ❌ BAD: Short or vague names
const id = rawMetadata.paymentContextId;
const flag = mapping.skipProfile === true;
const data = resolveInstanceConfig(config, mapping);
```

### Function Naming

```typescript
// ✅ GOOD: Verb-first names that describe behaviour
async function fetchAuthorizationToken(): Promise<string> { /* ... */ }
function buildAlertPayload(error: Error): AlertPayload { /* ... */ }
function isRetryableStatus(status: number): boolean { /* ... */ }

// ❌ BAD: Noun-only or ambiguous names
async function token(): Promise<string> { /* ... */ }
function payload(error: Error): AlertPayload { /* ... */ }
function status(value: number): boolean { /* ... */ }
```

### Function Structure

```typescript
// ✅ GOOD: Guard clauses and a clear main path
export async function processEvent(input: EventInput): Promise<EventOutput> {
  const eventId = input.eventId;

  if (!eventId) {
    throw new Error('Missing eventId');
  }

  const event = await loadEvent(eventId);
  const result = transformEvent(event);
  return persistEvent(result);
}

// ❌ BAD: Nested control flow hides the happy path
export async function processEvent(input: EventInput): Promise<EventOutput> {
  if (input.eventId) {
    const event = await loadEvent(input.eventId);
    if (event) {
      const result = transformEvent(event);
      return persistEvent(result);
    }
  }

  throw new Error('Invalid input');
}
```

### Immutability and Data Shaping

```typescript
// ✅ GOOD: Build new values explicitly
const updatedEvent = {
  ...event,
  status: 'processed',
};

const customerIds = records.map(record => record.customerId);

// ❌ BAD: Mutate shared state without a clear reason
event.status = 'processed';
records.push(newRecord);
```

### Error Handling

```typescript
function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

async function syncCustomer(customerId: string): Promise<void> {
  try {
    await sendCustomer(customerId);
  } catch (error: unknown) {
    logger.error('Failed to sync customer', {
      customerId,
      error: getErrorMessage(error),
    });
    throw new Error(`Failed to sync customerId=${customerId}`);
  }
}
```

### Operational Logging

| What | When | Level |
| --- | --- | --- |
| Workflow started or finished | Operators need to follow a production timeline | INFO |
| Success or skip outcome | State-changing or branch outcome needs completion evidence | INFO |
| Final workflow counters | Completion of an integration workflow | INFO |
| Performance timing | Integration latency measurement | INFO |
| Input request payload | Payload drives external calls or branching behaviour | DEBUG |
| Response payload | Outcome requires body detail | DEBUG |
| Mapping or decision logic | Conditional logic affects mapping or action | DEBUG |
| Extracted candidates | Engineers must validate duplicate detection, matching, or filtering | DEBUG |
| Retryable failure | Transient failure triggers retry handling | WARN |
| Terminal or unexpected failure | Failed operation, with sanitized request/response payloads when useful | ERROR |
| Transport internals | HTTP client connection noise with no business value | Suppress |

- Keep INFO logs to operational milestones, outcomes, counters, and elapsed
  timing. Do not put request bodies, response bodies, headers, URLs, or
  transport internals in INFO logs.
- Use DEBUG logs for payload-first troubleshooting when payloads materially
  affect branching behaviour, external interactions, mapping, matching, or
  decisions.
- Include sanitized request and response payloads in ERROR logs when those
  payloads are available and materially help troubleshoot the failure. Prefer
  the exact outbound request payload, useful upstream response body, upstream
  status, and retry decision over metadata-only errors.
- Prefer fewer, richer DEBUG logs over many fragmented metadata-only logs.
- Do not replace useful request/response payloads with derived field spam.
- Mask credential-like keys such as `token`, `authorization`, `appKey`,
  `apiKey`, `api_key`, `password`, and `secret` before logging payloads.
- Cap very large strings, arrays, and nested objects before they reach the shared
  log sink.
- Suppress or raise the level of noisy third-party transport loggers when they
  pollute workflow logs.
- Do not create generic data-shape helpers that guess alternative field names.
  Use the exact checked-in implementation contract, SDK type, or known upstream
  payload shape; fail clearly when that shape is absent.

When adding or refactoring workflow logging:

1. Identify the workflow milestones that belong at INFO.
2. Define stable correlation fields before adding log calls.
3. Log request and response payloads at DEBUG for external boundaries.
4. Log extracted candidates and selected records at DEBUG for matching,
   duplicate detection, or filtering.
5. Log the rules, thresholds, and reason for important branch decisions.
6. If the expected payload shape is absent, fail clearly or return the local
   controlled integration error instead of silently falling back to another
   shape.
7. Add or update tests for exact payload paths and important structured log
   fields when logs are part of the debugging contract.

```typescript
logger.info('Customer sync finished', {
  customerId,
  updatedCount,
  elapsedMs,
});

logger.debug('Customer sync request and response', {
  requestPayload: sanitizedRequestPayload,
  responsePayload: sanitizedResponsePayload,
  selectedRecordId,
  decisionReason,
});

logger.error('Customer sync failed', {
  customerId,
  error: getErrorMessage(error),
  requestPayload: sanitizedRequestPayload,
  responseStatus,
  responsePayload: sanitizedResponsePayload,
  retryable,
});
```

### Async/Await Best Practices

```typescript
// ✅ GOOD: Parallelise only independent work
const [retryPolicy, apiConfig] = await Promise.all([
  getRetryPolicy(),
  getApiConfig(),
]);

// ✅ GOOD: Keep dependent work sequential
const token = await fetchToken(apiConfig);
const response = await sendRequest(token);

// ❌ BAD: Unnecessary sequential waits for independent calls
const retryPolicy = await getRetryPolicy();
const apiConfig = await getApiConfig();
```

### Type Safety

```typescript
// ✅ GOOD: Narrow unknown input before use
function getCustomerId(value: unknown): string | null {
  if (!value || typeof value !== 'object') {
    return null;
  }

  const record = value as Record<string, unknown>;
  return typeof record.customerId === 'string' ? record.customerId : null;
}

// ❌ BAD: Skip narrowing
function getCustomerId(value: any): string {
  return value.customerId;
}
```

## Module Design

### Public API Shape

```typescript
// ✅ GOOD: Explicit contract and focused responsibility
export async function generateReceipt(
  input: ReceiptInput
): Promise<ReceiptOutput> {
  // ...
}

// ❌ BAD: Hidden inputs, hidden outputs, multiple responsibilities
export async function run(data: any): Promise<any> {
  // loads config, mutates globals, writes files, returns mixed shapes
}
```

### File Organization

```text
src/
├── workflow/
│   ├── client/
│   ├── server/
│   ├── types/
│   └── *.test.ts
├── utilities/
└── test-helpers/
```

- Group code by domain or workflow, not by arbitrary technical layers alone
- Keep shared utilities genuinely shared
- Co-locate tests with the behaviour they verify when practical

### Comments & Documentation

```typescript
// ✅ GOOD: Explains the reason for the choice
// Refresh config in the background so callers never wait on logging.
refreshLogLevel();

// ❌ BAD: Explains the obvious
// Call refreshLogLevel
refreshLogLevel();
```

Use JSDoc for exported utilities or shared helpers when the contract is not
obvious from the signature alone.

## Testing Standards

### Test Structure (AAA Pattern)

```typescript
test('throws when eventId is missing', async () => {
  // Arrange
  const input = { eventId: null };

  // Act
  const action = () => processEvent(input);

  // Assert
  await expect(action()).rejects.toThrow('Missing eventId');
});
```

### Test Naming

```typescript
// ✅ GOOD: Behaviour + condition
test('returns null when customerId is absent', () => { /* ... */ });
test('retries when the upstream API returns 429', () => { /* ... */ });

// ❌ BAD: Vague names
test('works', () => { /* ... */ });
test('handles input', () => { /* ... */ });
```

### Boundary Testing
- Test the happy path
- Test contract violations and missing required input
- Test dependency failures and retry decisions
- Restore globals, mocks, or environment changes after each test

## Code Smell Detection

### 1. Long or Multi-Purpose Functions
If one function validates input, reads config, transforms data, performs I/O,
formats logs, and builds output, it is doing too much.

### 2. Deep Nesting
Replace nested `if` blocks with guard clauses where possible.

### 3. Type Erosion
Watch for `any`, repeated casts, and outputs that drift away from declared
contracts.

### 4. Speculative Abstraction
Generic wrappers, helper factories, and indirection layers are a smell when the
code only has one real use case.

### 5. Hidden Boundary Behaviour
Do not bury network calls, filesystem writes, config reads, or retries inside
helpers with misleadingly simple names.

### 6. Contract Drift
If implementation, schema, tests, or metadata disagree, fix the drift rather
than papering over it in code.

### 7. Noisy or Weak Logs
Logs are weak when INFO carries payload bodies or transport chatter, DEBUG is
split into metadata fragments, or ERROR omits the sanitized request/response
payloads needed to understand the failure.

**Remember**: Strong TypeScript code is readable first, explicit at boundaries,
and boring in the best possible way.

## When to Use
Use this skill when writing or reviewing TypeScript and you need durable coding
standards that apply across codebases, especially around boundary logging,
error handling, and contract-driven implementation.

For PolyAPI-specific conventions, pair it with
[`coding-conventions`](../coding-conventions/SKILL.md).

## Limitations
- Use this skill for stable engineering standards, not framework-specific local
  rules.
- Prefer stronger project-local conventions when they exist.
- Do not treat this skill as a substitute for contract docs, tests, or runtime
  verification.
