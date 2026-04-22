# artefacts-usage Reference

## Folder layout for a workflow

```text
src/<workflow_name>/
  OVERVIEW.md
  server/
    <name>_sfx.py
  client/
    <name>_cfx.py
  types/
    <name>_types.py
  tests/
    test_<name>.py
  artefacts/
    webhooks/
      <name>_hook.json
    triggers/
      <name>_trigger.json
    vari/
      <name>_vari.json
    jobs/
      <name>_job.json
    tabi/
      <name>_tabi.json
    specs/
      <name>_spec.json
  deployment/
    <name>.sh
  scripts/
    <one_off_task>.py
```

## Folder layout for a shared utility

```text
src/utilities/<utility_name>/
  OVERVIEW.md
  server/
    <name>_sfx.py
  client/
    <name>_cfx.py
  types/
    <name>_types.py
  tests/
    test_<name>.py
  artefacts/
    vari/
      <name>_vari.json
    jobs/
      <name>_job.json
    tabi/
      <name>_tabi.json
    specs/
      <name>_spec.json
  deployment/
    <name>.sh
  scripts/
    <one_off_task>.py
```

## Webhook artefact

```json
{
  "name": "<name>_hook",
  "context": "<context.name>",
  "description": "<short description of what this endpoint does>",
  "subpath": "<url-path>?<param1>={<param1>}&<param2>={<param2>}",
  "method": "GET|POST|PUT|PATCH|DELETE",
  "eventPayloadType": "null",
  "responsePayload": {},
  "responseStatus": 200,
  "slug": "<project slug or token>",
  "xmlParserOptions": {
    "enabled": false,
    "explicitArray": false,
    "normalizeTags": false,
    "trim": false
  }
}
```

### Field rules

| Field | Rule |
| --- | --- |
| `name` | Must end with `_hook`. If the repo checks in trigger artefacts, keep the base name aligned with the paired trigger. |
| `context` | Must follow the target repo's naming conventions. |
| `subpath` | Must match the exact Mule public URL, including path params as `{param}` and query params as `?key={key}`. |
| `method` | Upper case. |
| `eventPayloadTypeSchema` | Full JSON Schema of the request body when the endpoint accepts a body. Omit it or use the repo's established empty-body pattern when there is no body. |
| `responsePayload` | Full JSON Schema of the success response body. |
| `responseStatus` | Preserve the Mule status code. |
| `slug` | Follow the checked-in repo convention. Preserve placeholder tokens when the repo uses them. |
| `xmlParserOptions.enabled` | Set to `true` only when the caller sends or receives XML. |

### XML parsing options

```json
"xmlParserOptions": {
  "enabled": true,
  "explicitArray": true,
  "trim": true,
  "normalizeTags": true
}
```

## Variable artefact

```json
{
  "name": "<name>_vari",
  "context": "<context.name>",
  "description": "<what this variable stores>",
  "value": "",
  "secret": false
}
```

## Job artefact

```json
{
  "name": "<flow_name>",
  "schedule": {
    "type": "periodical|interval",
    "value": "<cron expression or integer minutes>",
    "acceptableDelayTime": 30
  },
  "functions": [
    {
      "id": "<deployed function id>",
      "headersPayload": {},
      "eventPayload": {},
      "paramsPayload": {}
    }
  ],
  "enabled": true,
  "executionType": "sequential"
}
```

## Tabi artefact

```json
{
  "name": "<name>_tabi",
  "context": "<context.name>",
  "description": "<what this table contains>",
  "columns": [],
  "rows": []
}
```

## Shared placement guidance

- Put normal workflow implementations under `src/<workflow_name>/`.
- Put reusable cross-workflow code under `src/utilities/<utility_name>/`.
- Keep `scripts/` folders for one-off helper tasks local to the workflow or utility they support.

## OVERVIEW.md

Every workflow folder must have an `OVERVIEW.md` describing:

- integration purpose
- original Mule project it migrates
- PolyAPI components created
- required variables and secrets
- downstream systems
- behavioural parity notes
- known gaps or deviations
