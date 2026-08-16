# AI Function examples

Use these examples to reason from a stable contract, through initially adaptive implementation, toward evidence-based deterministic code. Always present the approval proposal first. Do not create the artefact until the user approves it.

- [Calculator: minimal and conditional](#calculator-minimal-and-conditional)
- [Weather companion: tools and variables](#weather-companion-tools-and-variables)
- [Supplier-order extraction](#supplier-order-extraction)
- [Integration-failure triage](#integration-failure-triage)

## Calculator: minimal and conditional

This is the simplest artefact example. It is a reasonable prototype when `operation` is intentionally open-ended: callers may use symbols, names, uncommon operations, or phrasing that has not been enumerated. If the supported operators are fixed—or numerical correctness is consequential—implement the calculation deterministically instead, or let AI interpret the request and delegate the arithmetic to a deterministic tool.

**Approval proposal:** I propose `calculator`. Input: `a`, `b`, and an open-ended operation. Output: a structured calculation result. Unenumerated operator names and notations make initial coverage uncertain; this is suitable only for a low-risk prototype, with deterministic calculation preferred when accuracy or the operator set is fixed. May I implement it?

After approval:

```json
{
  "name": "calculator",
  "context": "example.loop",
  "description": "Interprets an open-ended mathematical operation over two inputs and returns a structured result.",
  "visibility": "ENVIRONMENT",
  "state": "ALPHA",
  "enabled": true,
  "type": "TEXT",
  "provider": "openai",
  "apiType": "responses",
  "model": "gpt-5.5",
  "arguments": [
    {
      "key": "a",
      "type": "number",
      "required": true,
      "description": "The first numeric input."
    },
    {
      "key": "b",
      "type": "number",
      "required": true,
      "description": "The second numeric input."
    },
    {
      "key": "operation",
      "type": "string",
      "required": true,
      "description": "A mathematical operation expressed as a symbol, name, or natural-language instruction."
    }
  ],
  "systemPrompt": "Interpret the requested operation, apply it to a as the first input and b as the second input, and return the structured result. Never claim success when the operation is unsupported, ambiguous, or invalid.",
  "inputTemplate": "Perform {{operation}} using {{a}} and {{b}} as inputs.",
  "clientPromptEnabled": false,
  "clientPromptRequired": false,
  "clientPromptArgName": "",
  "toolFunctions": [],
  "outputSchema": {
    "type": "object",
    "additionalProperties": false,
    "required": ["success", "a", "b", "operation", "result", "error", "descriptionForModel"],
    "properties": {
      "success": { "type": "boolean" },
      "a": { "type": "number" },
      "b": { "type": "number" },
      "operation": { "type": "string" },
      "result": { "type": ["number", "null"] },
      "error": { "type": ["string", "null"] },
      "descriptionForModel": {
        "type": "string",
        "description": "A concise explanation naming the operation and showing how it was applied to the actual inputs."
      }
    }
  }
}
```

## Weather companion: tools and variables

The contract has a stable input—location and optional activity—and output—structured weather guidance—but locations, activities, weather combinations, and useful recommendations vary widely. Deterministic tools supply the weather facts; the AI Function resolves what to ask for and adapts the guidance. Over time, location normalization and recurring recommendation rules can move to code while AI remains only where contextual judgment adds value.

**Approval proposal:** I propose `upliftingWeather` at the weather-guidance boundary. Input: location and optional activity. Output: structured conditions and recommendations. The combinations of place, activity, and conditions make exhaustive response rules unstable; weather lookup remains tool-backed, and recurring normalization or advice can later become code. May I implement it?

After approval:

```json
{
  "name": "upliftingWeather",
  "context": "example.sampleAiFx",
  "description": "Returns accurate, practical, and encouraging weather guidance tailored to an optional activity.",
  "visibility": "ENVIRONMENT",
  "state": "ALPHA",
  "enabled": true,
  "type": "TEXT",
  "provider": "openai",
  "apiType": "responses",
  "model": "gpt-5.5",
  "arguments": [
    {
      "key": "location",
      "type": "string",
      "required": true,
      "description": "A village, city, region, country, or other location description."
    },
    {
      "key": "activity",
      "type": "string",
      "required": false,
      "description": "An optional activity for which the weather is relevant."
    }
  ],
  "systemPrompt": "Use the weather tools for all weather facts. Resolve the requested location, retrieve current conditions, and provide concise practical guidance tailored to the activity when supplied. Preserve safety warnings, avoid invented facts, and close with a brief sincere uplifting message.",
  "inputTemplate": "Provide weather guidance for {{location}} in the context of {{activity}} when supplied.",
  "clientPromptEnabled": false,
  "clientPromptRequired": false,
  "clientPromptArgName": "",
  "toolFunctions": [
    {
      "functionName": "search",
      "functionContext": "accuWeather.locations",
      "argumentConfig": [
        {
          "key": "locationText",
          "source": "ai"
        },
        {
          "key": "apiKey",
          "source": "variable",
          "variableName": "weatherApiKey",
          "variableContext": "example.sampleAiFx"
        }
      ]
    },
    {
      "functionName": "getByLocationKey",
      "functionContext": "accuWeather.currentConditions",
      "argumentConfig": [
        {
          "key": "locationId",
          "source": "ai"
        },
        {
          "key": "apiKey",
          "source": "variable",
          "variableName": "weatherApiKey",
          "variableContext": "example.sampleAiFx"
        }
      ]
    }
  ],
  "outputSchema": {
    "type": "object",
    "additionalProperties": false,
    "required": ["location", "currentWeather", "description", "recommendedItems", "upliftingMessage"],
    "properties": {
      "location": { "type": "string" },
      "currentWeather": {
        "type": "object",
        "additionalProperties": false,
        "required": ["condition", "temperature", "unit"],
        "properties": {
          "condition": { "type": "string" },
          "temperature": { "type": "number" },
          "unit": { "type": "string", "enum": ["C", "F"] }
        }
      },
      "description": { "type": "string" },
      "recommendedItems": {
        "type": "array",
        "items": { "type": "string" }
      },
      "upliftingMessage": { "type": "string" }
    }
  }
}
```

## Supplier-order extraction

The surrounding integration already knows what an order draft must contain, but it does not know which supplier layouts and conventions it will encounter.

| Design question | Answer |
|---|---|
| Stable contract | Input: `documentText`. Output: `PurchaseOrderDraft` with nullable evidence-based fields and warnings. |
| Unknown implementation space | Layouts, field labels, date and number formats, product descriptions, missing fields, tables damaged by OCR, and new supplier conventions |
| Initial value | Ship one bounded extractor instead of delaying the integration while writing speculative per-format parsers |
| Deterministic shell | Extract text, validate supplier/SKU/date/quantity/price/totals, reject or review uncertainty, and create the ERP order |
| Evidence to retain | Supplier/template family, AI output, validation failures, human corrections, latency, and cost—subject to data policy |
| Likely evolution | Generate parsers for frequent stable formats; use code for known labels and calculations; keep AI only for unseen or irregular documents, then remove it if the tail becomes negligible |

**Approval proposal:** I propose `extractSupplierOrder` between document ingestion and validation. Input: document text. Output: a strict purchase-order draft. Unknown supplier layouts and OCR variations make deterministic coverage unstable now; business validation and ERP creation remain in code, while observed formats can later become parsers. May I implement it?

After approval:

```json
{
  "name": "extractSupplierOrder",
  "context": "example.procurement",
  "description": "Extracts proposed normalized order data from varied supplier document text for deterministic validation.",
  "visibility": "ENVIRONMENT",
  "state": "ALPHA",
  "enabled": true,
  "type": "TEXT",
  "provider": "openai",
  "apiType": "responses",
  "model": "gpt-5.5",
  "arguments": [
    {
      "key": "documentText",
      "type": "string",
      "required": true,
      "description": "Text extracted from one supplier email, purchase order, or attachment."
    }
  ],
  "systemPrompt": "Extract only values supported by the supplied text. Do not infer identifiers, quantities, prices, or dates that are absent. Use null for an unknown scalar and an empty array when no line items are present. Record ambiguities and missing information in warnings.",
  "inputTemplate": "Extract the proposed supplier order from this document text:\n\n{{documentText}}",
  "clientPromptEnabled": false,
  "clientPromptRequired": false,
  "clientPromptArgName": "",
  "toolFunctions": [],
  "outputSchema": {
    "type": "object",
    "additionalProperties": false,
    "required": ["supplierReference", "orderDate", "currency", "lineItems", "warnings"],
    "properties": {
      "supplierReference": { "type": ["string", "null"] },
      "orderDate": { "type": ["string", "null"], "description": "ISO 8601 date when explicitly supported by the document." },
      "currency": { "type": ["string", "null"] },
      "lineItems": {
        "type": "array",
        "items": {
          "type": "object",
          "additionalProperties": false,
          "required": ["supplierSku", "description", "quantity", "unitPrice"],
          "properties": {
            "supplierSku": { "type": ["string", "null"] },
            "description": { "type": ["string", "null"] },
            "quantity": { "type": ["number", "null"] },
            "unitPrice": { "type": ["number", "null"] }
          }
        }
      },
      "warnings": { "type": "array", "items": { "type": "string" } }
    }
  }
}
```

## Integration-failure triage

The operations workflow can define the diagnosis it needs without knowing every provider, proxy, SDK, and network error representation that production will expose.

| Design question | Answer |
|---|---|
| Stable contract | Input: `executionId`. Output: `FailureDiagnosis` with domain, evidence, probable cause, next steps, and confidence. |
| Unknown implementation space | Provider-specific bodies, nested errors, aliases, SDK wrapping, version changes, misleading status codes, and interacting failures |
| Initial value | Provide useful structured triage before building a comprehensive error catalogue and rules engine |
| Deterministic shell | Retrieve and redact evidence, validate the diagnosis, enforce retry/routing policy, alert, and perform remediation |
| Evidence to retain | Sanitized error signature, diagnosis, actual resolution, operator correction, recurrence, latency, and cost |
| Likely evolution | Convert recurring signatures and resolutions into direct rules; route only unknown or conflicting evidence to a smaller AI Function |

**Approval proposal:** I propose `triageIntegrationFailure` between execution failure and incident routing. Input: an execution reference. Output: a strict diagnosis. Unseen provider errors and wrappers make a complete rules engine speculative now; routing, retries, and remediation remain deterministic, while recurring signatures can later become code. May I implement it?

After approval:

```json
{
  "name": "triageIntegrationFailure",
  "context": "example.operations",
  "description": "Produces a structured proposed diagnosis for varied integration failures.",
  "visibility": "ENVIRONMENT",
  "state": "ALPHA",
  "enabled": true,
  "type": "TEXT",
  "provider": "openai",
  "apiType": "responses",
  "model": "gpt-5.5",
  "arguments": [
    {
      "key": "executionId",
      "type": "string",
      "required": true,
      "description": "The failed integration execution to inspect."
    }
  ],
  "systemPrompt": "Use the execution-details tool as the only source of facts. Distinguish observed evidence from the probable cause. Never expose credentials or claim that a retry or remediation occurred. Recommend concise next steps for deterministic routing or human review.",
  "inputTemplate": "Triage failed integration execution {{executionId}}.",
  "clientPromptEnabled": false,
  "clientPromptRequired": false,
  "clientPromptArgName": "",
  "toolFunctions": [
    {
      "functionName": "getExecutionDetails",
      "functionContext": "example.integrations",
      "argumentConfig": [
        {
          "key": "executionId",
          "source": "argument",
          "argumentKey": "executionId"
        },
        {
          "key": "apiKey",
          "source": "variable",
          "variableName": "integrationApiKey",
          "variableContext": "example.config"
        }
      ]
    }
  ],
  "outputSchema": {
    "type": "object",
    "additionalProperties": false,
    "required": ["summary", "domain", "observedEvidence", "probableCause", "recommendedNextSteps", "confidence"],
    "properties": {
      "summary": { "type": "string" },
      "domain": {
        "type": "string",
        "enum": ["authentication", "authorization", "rate_limit", "validation", "network", "provider", "unknown"]
      },
      "observedEvidence": { "type": "array", "items": { "type": "string" } },
      "probableCause": { "type": "string" },
      "recommendedNextSteps": { "type": "array", "items": { "type": "string" } },
      "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
    }
  }
}
```
