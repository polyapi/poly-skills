# MCP server examples

Use these examples to move from an audience and a set of existing functions to
a reviewed tool surface. Always present the approval proposal first. Do not
create the artefact until the user approves it.

- [Read-only weather tools](#read-only-weather-tools)
- [Support desk with a guarded write](#support-desk-with-a-guarded-write)
- [Partner access with OAuth](#partner-access-with-oauth)
- [Narrowing an over-broad request](#narrowing-an-over-broad-request)

## Read-only weather tools

Two trained Open-Meteo API Functions already exist in `example.weather`. The
client should resolve places and read current conditions; the provider hosts
and units must stay fixed.

**Approval proposal:** I propose MCP server `example-weather-tools` for the
team's coding assistants with `searchLocations` and `getCurrentWeather`. The
client chooses the place name and coordinates; provider hosts, result count,
and Celsius stay fixed through bindings. All tools are read-only. May I create
it?

After approval, `artefacts/mcp-servers/weatherTools.json`:

```json
{
  "name": "example-weather-tools",
  "description": "Find a location and read its current weather from Open-Meteo.",
  "enabled": true,
  "isPublic": false,
  "toolFunctions": [
    {
      "functionName": "searchLocations",
      "functionContext": "example.weather",
      "argumentConfig": [
        { "key": "name", "source": "ai" },
        { "key": "hostUrl", "source": "hardcoded", "value": "https://geocoding-api.open-meteo.com" },
        { "key": "count", "source": "hardcoded", "value": 3 },
        { "key": "language", "source": "hardcoded", "value": "en" },
        { "key": "format", "source": "hardcoded", "value": "json" }
      ]
    },
    {
      "functionName": "getCurrentWeather",
      "functionContext": "example.weather",
      "argumentConfig": [
        { "key": "latitude", "source": "ai" },
        { "key": "longitude", "source": "ai" },
        { "key": "hostUrl", "source": "hardcoded", "value": "https://api.open-meteo.com" },
        { "key": "current", "source": "hardcoded", "value": "temperature_2m,precipitation,weather_code,wind_speed_10m" },
        { "key": "temperatureUnit", "source": "hardcoded", "value": "celsius" },
        { "key": "timezone", "source": "hardcoded", "value": "auto" }
      ]
    }
  ]
}
```

Bind keys to the trained function's argument names, which can differ from the
provider's parameters: the platform translator turns `temperature_unit` into
`temperatureUnit`. Check the saved `.poly.json` model before binding.

## Support desk with a guarded write

The user asks for ticket tools for support agents, including status changes.
API Functions `getTicket`, `searchTickets`, `updateTicket`, and `deleteTicket`
exist in `example.support`; each takes an `apiKey`.

| Design question | Answer |
|---|---|
| Read tools | `getTicket` and `searchTickets`, with the key bound from vari |
| Write need | Change a ticket's status |
| Why not `updateTicket` | It accepts any field, so the model could rewrite assignees, requesters, or text |
| Guard | A server function `setTicketStatus` that allows only `open`, `pending`, and `solved` and requires a reason |
| Excluded | `deleteTicket`: permanent, and ticket text is customer-written input the model may follow |

**Approval proposal:** I propose MCP server `example-support-desk` for support
agents with `getTicket`, `searchTickets`, and a new `setTicketStatus` server
function. The client chooses ticket IDs, search text, a status from three
allowed values, and a reason; the Zendesk key stays in vari. `setTicketStatus`
is the only write, and `deleteTicket` and the general `updateTicket` stay out.
May I create the server function and the MCP server?

After approval, implement and test `setTicketStatus` first, then
`artefacts/mcp-servers/supportDesk.json`:

```json
{
  "name": "example-support-desk",
  "description": "Read support tickets and move them between open, pending, and solved.",
  "enabled": true,
  "isPublic": false,
  "toolFunctions": [
    {
      "functionName": "getTicket",
      "functionContext": "example.support",
      "argumentConfig": [
        { "key": "ticketId", "source": "ai" },
        { "key": "apiKey", "source": "variable", "variableName": "zendeskApiKey", "variableContext": "example.support" }
      ]
    },
    {
      "functionName": "searchTickets",
      "functionContext": "example.support",
      "argumentConfig": [
        { "key": "query", "source": "ai" },
        { "key": "apiKey", "source": "variable", "variableName": "zendeskApiKey", "variableContext": "example.support" }
      ]
    },
    {
      "functionName": "setTicketStatus",
      "functionContext": "example.support",
      "argumentConfig": [
        { "key": "ticketId", "source": "ai" },
        { "key": "status", "source": "ai" },
        { "key": "reason", "source": "ai" }
      ]
    }
  ]
}
```

`setTicketStatus` reads the key from vari itself, so the MCP binding has none.

## Partner access with OAuth

A partner's assistant needs read access to order status. The user has
registered an OAuth client for it and stored the client secret in vari.

**Approval proposal:** I propose MCP server `example-partner-orders` for the
partner's assistant with `getOrderStatus` only. The client chooses an order
number; the OAuth client `partner-orders` and its secret in vari control
access, and the tool is read-only. Private servers accept only OAuth sign-ins,
not PolyAPI keys, and I have not yet seen this sign-in work, so I will confirm
it with a test connection before you share the URL. May I create it?

After approval, the SECRET vari placeholder
`artefacts/vari/partnerOauthSecret.json` (the value is set in PolyAPI, never
committed), using the project's vari artefact format, and
`artefacts/mcp-servers/partnerOrders.json`:

```json
{
  "name": "example-partner-orders",
  "description": "Look up the status of a partner's order by order number.",
  "enabled": true,
  "isPublic": false,
  "oauthClientId": "partner-orders",
  "oauthClientSecretVariable": {
    "variableName": "partnerOauthSecret",
    "variableContext": "example.partners"
  },
  "oauthRedirectUris": ["https://assistant.partner.example/oauth/callback"],
  "toolFunctions": [
    {
      "functionName": "getOrderStatus",
      "functionContext": "example.orders",
      "argumentConfig": [{ "key": "orderNumber", "source": "ai" }]
    }
  ]
}
```

Use `null` for `oauthClientId` or `oauthClientSecretVariable` to clear them.

## Narrowing an over-broad request

The user asks: "Expose all our CRM functions over MCP and make it public so
the sales team can use it from anywhere."

Do not create it as asked. The context contains create, update, merge, and
delete operations, and a public endpoint widens who can reach them.

**Approval proposal:** I propose MCP server `example-sales-lookup` for the
sales team with `searchAccounts`, `getAccount`, and `listOpenOpportunities`.
The client chooses search text and account IDs; the CRM key stays in vari. All
tools are read-only. The server stays private, so the sales team can connect
only through an OAuth client; tell me which one to configure. Merges, deletes,
and updates remain outside MCP until there is a validated server function for a
specific change. A public server would let anyone with its URL call these tools,
so tell me who will connect before choosing that. May I create it?
