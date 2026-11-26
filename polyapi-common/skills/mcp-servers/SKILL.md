---
name: mcp-servers
description: Use when exposing PolyAPI functions as tools to external AI clients, coding agents, or chat assistants over the Model Context Protocol (MCP); also use when creating, updating, reviewing, or debugging Flow MCP server artefacts, their tool bindings, OAuth settings, or public visibility.
---

# MCP Servers

## Core mental model

An MCP server is a published tool surface: a curated set of existing PolyAPI
functions that an external model can discover and call. The reasoning happens
outside PolyAPI, in a client you do not control, such as Claude, an IDE agent,
or a partner's assistant. PolyAPI lists the tools, binds fixed and secret
arguments, executes the calls, and authenticates the connection.

| | AI Function | MCP server |
|---|---|---|
| Who reasons | A PolyAPI-hosted model with your prompt | The client's model, with its own prompt |
| Your contract | Arguments, prompt, tools, strict output schema | Each tool function's own name, description, and arguments |
| How you steer it | `systemPrompt` and `outputSchema` | Tool selection, descriptions, and fixed bindings only |
| Typical use | A step inside your workflow | Offering capabilities to agents or users outside it |

Ask the central question:

> **Which existing functions may an external model call, with which inputs left to its choice, and what must stay fixed or behind deterministic code?**

Treat every tool call as untrusted input chosen by a model you cannot inspect.
Content the tools return, such as tickets, emails, or documents, can carry
instructions that the client's model may follow.

## Find the right boundary

Ask in order:

1. **Who connects, and why?** Name the client and audience. One focused server
   per audience beats one server exposing everything; long tool lists degrade
   tool selection.
2. **Which functions are tools?** Prefer read-only, idempotent, bounded calls.
   Reuse existing API or server functions in the server's own environment; an
   MCP server does not create new behavior. Client functions run in the
   caller's process, and functions shared from other environments are out of
   the endpoint's reach, so neither can be an MCP tool.
3. **What must the model not choose?** Hosts, tenants, accounts, limits, and
   credentials. Bind them with `hardcoded` values or namespace-owned `variable`
   references; leave only genuine user intent as `ai` arguments.
4. **Is any tool consequential?** Writes, deletes, payments, messages, and
   permission changes need a server function that validates input, enforces
   authorization and limits, and refuses unsafe requests. Never expose a raw
   delete or bulk-update API function.
5. **Will the model understand each tool?** The client sees the function's
   name, description, and argument descriptions. Fix vague or misleading
   descriptions in the function before exposing it.
6. **How is access controlled?** Keep `isPublic` false unless a public endpoint
   is an explicit requirement: anyone with a public server's URL can call its
   tools. A private server accepts only OAuth sign-ins, so it is unusable until
   it has OAuth settings. Configure OAuth only with a client the user names, and
   keep its secret in a `SECRET` vari.
7. **Is the namespace safe to show?** Tool names include the function's
   context, so every client sees it.

Do not use an MCP server to give your own workflow model access to tools; that
is an AI Function. Do not use one to replace a webhook or API for deterministic
system-to-system integration.

## Know what is verified

The platform API defines servers by `name`, `description`, `enabled`,
`isPublic`, tool functions with argument bindings, and OAuth client settings.
Servers have no namespace context. `GET /mcp-servers/{id}` returns the server's
`mcpUrl`, `https://<instance>/mcp-servers/<id>/mcp`.

Verified on a live PolyAPI instance:

- Clients see each tool as its context and name joined with underscores, such
  as `example_weather_searchLocations`, described by the function's own
  description. Only `ai` arguments are tool inputs; other bindings stay hidden.
- `isPublic: true`: any client with the URL can list and call the tools without
  signing in.
- `isPublic: false`: anonymous requests get 403, and PolyAPI keys get 401
  ("Invalid OIDC access token"); clients must sign in with OAuth. Without OAuth
  settings, the server advertises no authorization server, so no client can
  sign in.
- When `oauthRedirectUris` is omitted, PolyAPI adds the claude.ai and ChatGPT
  connector callbacks.

A complete OAuth sign-in has not been verified. Before telling a user how their
team will sign in, verify it against the target environment or the platform
team.

## Mandatory approval gate

Never create an MCP server, add tools to one, add a consequential tool, add or
change OAuth settings, or set `isPublic: true` without the user's explicit,
informed approval.

Before writing or modifying the artefact, give a brief approval request,
normally two or three sentences. State the audience, the exact tools, what
the model chooses versus what is fixed, and any consequential or public
exposure. Push back on raw destructive tools and unneeded public access. Then
ask: **May I create this MCP server?** Stop and wait.

Use this shape:

> I propose MCP server `[name]` for `[audience]` with `[tools]`. The client chooses `[ai arguments]`; `[hosts/credentials/limits]` stay fixed through bindings. `[Consequential or public exposure, or "All tools are read-only"]`. May I create it?

An instruction to "just deploy it" or an earlier mention of MCP does not count
as approval after your proposal. Reviewing or diagnosing an existing server
needs no approval.

## Implement with Flow

Check the project's Flow version: TypeScript Flow 1.2.1
(`pnpm flow run version`) or Python Flow 1.3.2
(`uv run --locked python cli/flow.py --version`) or newer. Older versions cannot deploy MCP servers, or can leave removed tools
callable and accept tools the MCP endpoint cannot call. If the version is older,
stop and tell the user; do not hand-write API calls or commit remote IDs to work
around it.

Put each server in `workflows/src/<workflow>/artefacts/mcp-servers/<name>.json`:

- `name` must be unique in the target environment. Flow matches servers by
  exact name, fails on duplicates, and never reports or deletes MCP servers as
  orphans, so remove retired servers deliberately in PolyAPI.
- Reference tools with `functionName` and `functionContext`. They must be API
  or server functions in the target environment; Flow rejects client functions
  and functions shared from other environments before writing.
- `toolFunctions` is the server's complete tool list: removing an entry removes
  the tool, and Flow clears legacy `toolFunctionIds` that would keep old tools
  callable. Flow compares each `hardcoded` value whole, so removing a property
  from a JSON value updates the deployed binding.
- Use `argumentConfig` sources `ai`, `hardcoded`, `argument`, or `variable`.
  Keep `variableContext` inside `POLYAPI_NAMESPACE`.
- For OAuth, use `oauthClientId`, `oauthRedirectUris`, and
  `oauthClientSecretVariable` with `variableName` and `variableContext`.
- Never write `toolFunctionIds`, `oauthClientSecretVariableId`,
  `environmentId`, `mcpUrl`, or tool `id` values.

Add an offline test that pins the reviewed tool list, `isPublic`, and the fixed
bindings, so widening the server fails review. Deploy the tool functions
first, preview, then push only the servers. In a TypeScript project:

```bash
pnpm workflows push --dry-run --paths <workflow> --types mcp-servers
pnpm workflows push --paths <workflow> --types mcp-servers
```

In a Python project:

```bash
uv run --locked python cli/flow.py push --paths <workflow> --types mcp-servers --dry-run
uv run --locked python cli/flow.py push --paths <workflow> --types mcp-servers
```

Flow prints each server's MCP URL. Verify with a real MCP client or the
[MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector): list
the tools, call a read-only tool, and inspect the function's execution logs.

Read [references/examples.md](references/examples.md) before proposing or
implementing an MCP server. It contains approval proposals and valid
artefacts.

## Common mistakes

| Mistake | Instead |
|---|---|
| Exposing every function in a context | Pick the few tools the audience needs |
| Raw delete, bulk, or payment API functions as tools | A validating server function with explicit limits, or no tool |
| Letting the model choose `hostUrl`, tenant, or account IDs | `hardcoded` or `variable` bindings |
| Sharing a private server without OAuth settings | Configure the OAuth client first; PolyAPI keys are not accepted |
| Promising how users will sign in | Verify the OAuth sign-in in the target environment |
| `isPublic: true` for convenience | Keep it false unless public access is a stated requirement |
| Reusing a server name from another project | A name unique in the environment |
| Expecting Flow to delete a removed artefact's server | Delete it deliberately in PolyAPI |
