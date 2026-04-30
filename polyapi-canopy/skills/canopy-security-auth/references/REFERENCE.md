# Canopy Security and Auth Reference

## Sensitive Data Rules

Avoid reading or exposing:

- `.env`, `.env.*`
- `*.key`, `*.pem`, `*.p12`, `*.pfx`, `*.crt`
- API keys, bearer tokens, cookies, session secrets
- MFA/OTP values
- customer payloads or concrete tenant/user/application debug IDs unless
  explicitly safe and sanitized

Prefer field names and behavior descriptions over real values.

## Auth and Session Files

Key files:

- `src/components/session/actions.ts` - login, logout, session bootstrap,
  access-log writes.
- `src/components/session/IdleHandler.tsx` - client-side idle timer that
  triggers logout/refresh.
- `src/components/session/LogoutButton.tsx` - logout UI.
- `src/components/auth/MfaTokenDialog.tsx`,
  `src/components/auth/MfaTokenInput.tsx` - MFA prompt UI.
- `src/api/session.ts` - cookie names (`COOKIE_NAME_SESSION_ID`,
  `POLY_COOKIE_SESSION_ID`), basePath-aware cookie path, default-app shadow
  cookie.
- `src/api/poly/auth.ts` - API key, session/auth data lookup.
- `src/api/poly/types.ts` - `User`, `UserRole`, `AuthData`, `WhoamiData`,
  `ClientAuthData`, `SessionConfig`.
- `src/api/poly/common.ts` - `processResponse`, `RawResponseHolder`,
  `getWithAuth`.
- `src/api/poly/config.ts` - app config + session config loading.
- `src/api/poly/whoami.ts`, `app.ts` - current user and configured
  applications.
- `src/lib/session.ts` - JWT-encrypted session payload stored in Redis;
  `createSession`, `updateSession`, `getSession`, `deleteSession`,
  `refreshSession` enforce `idleTimeout` and `maxTimeout`.
- `src/lib/redis.ts` - ioredis client with optional TLS via `./tls/ca.crt`,
  `tls.crt`, `tls.key`.
- `src/middleware.ts` - request logging, `x-url` header.
- `src/hooks/useAuth.ts` - client auth hook.

Current login facts:

- Invalid key UX message is `Invalid API key.`.
- Login-time `401` and `403` are treated as invalid API key.
- `startAuthenticatedSession` rejects payloads missing `apiKeyId`,
  `tenant.id`, or `environment.id`.
- `startAuthenticatedSession` rejects missing `authData.user.id`.
- Failures can mark `accessLogWritten: true` to prevent duplicate logging.
- `processResponse` can return `null` for `204` or zero-length responses,
  even when callers use typed generics.

Session lifetime:

- Session is JWT-encrypted with `SESSION_SECRET` and stored at
  `canopy:session:<sessionId>` in Redis.
- TTL is initially `idleTimeout` minutes; refreshed on activity up to
  `maxTimeout` minutes from `sessionStart`.
- Do not bypass `refreshSession` capping logic; total session lifetime must
  not exceed `maxTimeout`.

## Access Logs

Key files:

- `src/components/session/actions.ts`
- `src/api/poly/collection.ts`
- `polyapi_config/collections/access-logs/collection.json`
- `polyapi_config/collections/access-logs/api.json`

Storage keys written by `logSystemAccess`:

- `system-access:tenant:<tenantId-or-null>:<date>:<id>`
- `system-access:user:<user-or-subject-id>:<date>:<id>`
- `system-access:application:<applicationId>:<date>:<id>`

Unknown-tenant failures use `tenant:null`:

- `system-access:tenant:null:*`

`src/api/poly/collection.ts` merges unknown failures into Access Logs only for
the `access-logs` collection. When status is selected, unknown failures are
included only for `failure`.

Access Logs status values:

- `success`
- `failure`

Do not send empty `status=`; omit the param.

Identity fields:

- `ClientAuthData.ssoUserId`
- `WhoamiData.ssoUserId`
- `User.ssoId`
- access-log entry field `ssoSubjectId`

Never log the API key itself. Use a non-secret SSO subject/user identifier when
available.

## Role Model

From `src/api/poly/types.ts`:

```ts
User.role: UserRole
```

Roles:

- `SUPER_ADMIN`
- `ADMIN`
- `USER`

`src/components/collection/utils.ts` ranks roles as:

- `SUPER_ADMIN` = 2
- `ADMIN` = 1
- `USER` = 0

Use `auth.user.role`, not `auth.user.roles`.

## Visibility and Editability

`requiredRole`:

- filters fields out for users below the required role
- useful when a field should not appear in a context

`dynamic.readOnly`:

- keeps the field visible but locked
- useful when unauthorized users should still see the value

Server function runtime settings example:

- `sleepCycleInterval`
- `limitTime`
- current expression: `auth?.user?.role !== 'SUPER_ADMIN'`

Check backend enforcement separately for sensitive writes.

## API Keys, Permissions, and Claims

Current checked-in state:

- API key `permissions` is a fixed `nested` boolean schema.
- API key config/API spec do not currently include `claims`.

Future claims guidance:

- If backend/API confirms arbitrary claims, model them as `type: "json"`.
- Use `readOnly: true` for display-only claims.
- Keep About Me SSR page and client dialog in sync:
  - `src/app/about-me/page.tsx`
  - `src/app/about-me/AboutMeButton.tsx`
- Preserve backend PATCH semantics; do not invent client-side merge behavior.

## MFA and Raw Execution

MFA token is sensitive. Do not log it or move it into client-only code.

UI:

- `src/components/auth/MfaTokenDialog.tsx`,
  `src/components/auth/MfaTokenInput.tsx` collect the OTP.
- `src/components/action-bar/MfaActionButton.tsx` triggers MFA-gated actions.

For raw functions:

- `executeRawFunction` sets `x-otp` only when `mfaToken` is passed as the
  final argument.
- `getExecutionBody(..., mfaToken)` only includes it in the body if config
  maps it.
- Raw functions bypass the function gateway, so gateway middleware will not
  add missing headers.

## Auth Callback and Key Lifecycle Routes

`src/app/[appId]/auth/[[...params]]/` is a catch-all that handles auth
callbacks and key-lifecycle UX. Related routes/components:

- `src/app/[appId]/auth/expired/`,
  `src/app/[appId]/auth/expiring/`,
  `src/app/[appId]/auth/rotated/` - key state pages.
- `src/app/[appId]/auth/finish-oauth/` - OAuth completion handler.
- `src/app/[appId]/auth/choose-environment/` - environment selection after
  multi-env login.
- `src/app/[appId]/auth/GenerateNewKeyButton.tsx` - regenerate API key UI.
- `src/app/ExpiringKeyWarning.tsx` - global expiring-key banner.
- `src/app/[appId]/login/`, `src/app/[appId]/signup/` - login and signup
  flows configured from `polyapi_config/app_base.json`.
- `src/app/[appId]/unauthorized/` - unauthorized landing.

Treat all of these as security-sensitive when changing copy, redirects, or
state transitions.

