# Catalog

| Area | Type | Item | Notes |
| --- | --- | --- | --- |
| `boomi-to-polyapi` | Pack | `AGENTS.md` | Shared migration rules |
| `boomi-to-polyapi` | Agent | `specialised_agents/BOOMI_ARCHITECT.md` | Boomi source analysis and manifest generation |
| `boomi-to-polyapi` | Agent | `specialised_agents/POLYAPI_CODEAGENT.md` | PolyAPI TypeScript implementation orchestration |
| `boomi-to-polyapi` | Skill | `boomi-download-source` | Download raw Boomi component XML and metadata |
| `boomi-to-polyapi` | Skill | `boomi-compress-source` | Compress Boomi XML into compact evidence for analysis |
| `boomi-to-polyapi` | Skill | `boomi-to-polyapi-conversion` | Stage-3 conversion workflow, playback, and approval gates |
| `boomi-to-polyapi` | Skill | `naming-conventions-boomi` | Naming rules for Boomi-derived workflows, artifacts, and contexts |
| `boomi-to-polyapi` | Skill | `generate-schemas-boomi` | Derive JSON Schemas from Boomi profiles and operations |
| `mulesoft-to-polyapi` | Pack | `AGENTS.md` | Shared migration rules |
| `mulesoft-to-polyapi` | Agent | `specialised_agents/MULE_ARCHITECT.md` | MuleSoft analysis and manifest generation |
| `mulesoft-to-polyapi` | Agent | `specialised_agents/POLYAPI_CODEAGENT.md` | Generic PolyAPI implementation orchestration |
| `mulesoft-to-polyapi` | Skill | `compress-source` | Compress Mule XML and RAML into migration artefacts |
| `mulesoft-to-polyapi` | Skill | `extract-redact-mule-jars` | Unpack Mule jars and redact configuration |
| `mulesoft-to-polyapi` | Skill | `generate-schemas` | Generate JSON Schemas and optional Python helper classes from RAML |
| `polyapi-common` | Skill | `ai-functions` | Design approved AI Function boundaries when contracts are known but scenarios are not, then evolve them from logs toward deterministic code |
| `polyapi-common` | Skill | `design-analysis` | Interpret PolyAPI design diagrams |
| `polyapi-common` | Skill | `generate-overview` | Refresh same-folder `OVERVIEW.md` files |
| `polyapi-common` | Skill | `polyapi-implementation-principles` | Shared PolyAPI implementation principles for architecture-sensitive repo changes |
| `polyapi-common` | Skill | `polyapi-constructs` | Language-agnostic definitions and decision rules for PolyAPI constructs (schemas, webhooks, triggers, functions, jobs, vari, tabi, canopy) |
| `polyapi-common` | Skill | `canopy-ui` | Customer-facing Canopy app authoring through Application JSON: collections, forms, actions, argument mapping, and deployment via PolyUI |
| `polyapi-common` | Skill | `tabi` | Design, create, query, review, and maintain PolyAPI Tabi tables, SDK row operations, and lifecycle state |
| `polyapi-python` | Guide | `AGENTS.md` | Generalized root agent guide for PolyAPI Python repos |
| `polyapi-python` | Skill | `polyapi-sdk` | Python SDK and typing quirks |
| `polyapi-python` | Skill | `coding-conventions` | Python naming and file-layout conventions |
| `polyapi-python` | Skill | `artefacts-usage` | Python artefact structure and placement |
| `polyapi-python` | Skill | `coding-standards` | Python logging and error-handling rules |
| `polyapi-typescript` | Guide | `AGENTS.md` | Generalized root agent guide for PolyAPI TypeScript repos |
| `polyapi-typescript` | Skill | `polyapi-sdk` | TypeScript PolyAPI runtime and sync rules |
| `polyapi-typescript` | Skill | `polyapi-runtime-testing` | TypeScript deployed-function integration testing and log verification |
| `polyapi-typescript` | Skill | `coding-conventions` | TypeScript PolyAPI conventions |
| `polyapi-typescript` | Skill | `artefacts-usage` | TypeScript artefact structure and placement |
| `polyapi-typescript` | Skill | `coding-standards` | TypeScript implementation standards |
| `general` | Skill | `markdownlint-compliance` | Markdown authoring rules |
| `general` | Skill | `clean-code` | General engineering reference |

Internal maintainer guidance lives under `.agents/skills/` and is not part of
the public catalog.
