---
name: canopy-security-auth
description: Use when changing Canopy auth, sessions, access logs, roles, permissions, visibility, read-only behavior, API key display, claims, MFA, tenant isolation, or any security-sensitive UI/runtime behavior.
---

# Canopy Security and Auth

## Overview

Security-sensitive Canopy work includes auth/session behavior, Access Logs,
roles, permissions, API keys, claims, MFA, tenant boundaries, and role-based UI.
Frontend visibility is not server-side enforcement, and config-driven UI makes
that separation easy to miss.

## Quick Rules

- Never expose secrets, API keys, MFA/OTP tokens, credentials, private keys, or
  sensitive customer data.
- Avoid reading `.env`, key, cert, or secret files unless explicitly required
  and safe.
- Start login/access-log changes in `src/components/session/actions.ts`.
- Validate auth payload shape before reading nested fields.
- Login-time `401` and `403` map to `Invalid API key.` in this repo's login UX.
- A key without `authData.user.id` is a failed login, not a partial success.
- Never write the API key value into access logs.
- Unknown-tenant auth failures still need Access Logs visibility.
- Check `src/api/poly/types.ts` before role/auth expressions.
- Current user model uses singular `user.role`, not `user.roles`.
- Distinguish hidden fields (`requiredRole`) from visible read-only fields
  (`dynamic.readOnly`).
- Verify backend authorization for sensitive updates; frontend hiding is not
  enough.
- Sessions are JWT-encrypted in Redis with `idleTimeout` / `maxTimeout` from
  `SessionConfig`; never bypass `refreshSession` capping.
- Session cookies are basePath-aware; the default app sets a shadow
  `POLY_COOKIE_SESSION_ID` cookie used by top-level routes.

## Workflow

1. Identify what data/action becomes visible, editable, logged, or transmitted.
2. Inspect current auth/session/type contracts in `src/api/poly/types.ts` and
   `src/components/session/actions.ts`.
3. Inspect relevant collection config and API spec for role/read-only/schema
   behavior.
4. Decide whether unauthorized users should see nothing, see disabled UI, see
   read-only UI, or be server-restricted.
5. For Access Logs, verify storage/merge behavior, status values, and optional
   filter omission.
6. For MFA/raw execution, verify token transport without logging or exposing the
   token.
7. Validate backend enforcement where a direct API call could bypass the UI.
8. Run targeted diagnostics.

## Common Mistakes

- Logging API keys or OTP values.
- Assuming auth payloads are always well-formed.
- Creating sessions for key-without-user states.
- Dropping auth failures because tenant resolution failed.
- Writing `auth.user.roles.includes(...)`.
- Treating `requiredRole` and `dynamic.readOnly` as interchangeable.
- Assuming API schema support proves authorization is enforced.
- Modeling dynamic claims as fixed permission booleans.

## Reference

See [references/REFERENCE.md](./references/REFERENCE.md) for auth/access-log
flow, role model, API key claims notes, and sensitive file guidance.

