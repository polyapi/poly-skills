# Tabi Implementation Reference

Use this reference when creating or updating a Tabi table, implementing SDK row
operations, or checking a design against current platform limits.

## Table Creation Contract

Create tables through Manage Tabi Tables or `POST /tables` in the target
environment's Swagger. A representative payload is:

```json
{
  "name": "CustomerState",
  "context": "customer.data",
  "description": "Workflow state keyed by the upstream customer identifier",
  "visibility": "ENVIRONMENT",
  "columns": [
    {
      "name": "external_id",
      "type": "text",
      "required": true,
      "unique": true,
      "primary": false,
      "schema": { "type": "string" }
    },
    {
      "name": "data_type",
      "type": "text",
      "required": true,
      "unique": false,
      "primary": false,
      "schema": {
        "type": "string",
        "enum": ["building", "company", "user"]
      }
    },
    {
      "name": "json_data",
      "type": "jsonb",
      "required": true,
      "unique": false,
      "primary": false,
      "schema": { "type": "object" }
    }
  ]
}
```

`ownerUserId` is optional in the API and defaults from the authenticated user
when the platform can resolve one. Confirm visibility and ownership expectations
for the target environment.

Tabi adds these reserved columns:

| Column | Type | Behavior |
| --- | --- | --- |
| `id` | `uuid` | Generated primary key |
| `createdAt` | `timestamptz` | Set when the row is inserted |
| `updatedAt` | `timestamptz` | Updated by the platform trigger |

Current canonical column types documented for table contracts are `bigint`,
`boolean`, `date`, `float`, `integer`, `jsonb`, `numeric`, `text`, `time`,
`timestamptz`, and `uuid`. The service accepts some aliases, but prefer the
canonical names and verify the current environment's Swagger before relying on
an alias.

## Column Semantics

| Field | Meaning |
| --- | --- |
| `name` | Top-level row field and generated SDK property |
| `type` | Enforced PostgreSQL storage type |
| `required` | Adds `NOT NULL` when true |
| `unique` | Adds a per-column unique constraint |
| `primary` | Reserved for the platform-owned `id` primary key |
| `default` | Database default; cannot be changed later |
| `schema` | Generated SDK type hints and documentation only |

JSON Schema does not validate inserted values beyond the database-level column
contract. For example, an enum in `schema` improves generated types but does not
create a PostgreSQL enum or runtime check constraint.

PostgreSQL permits multiple `NULL` values in a unique column. Set `required` if
every row must have the unique key used for lookup or upsert.

## Schema Evolution

| Change | Supported |
| --- | --- |
| Add a column | Yes |
| Drop a non-reserved column | Yes |
| Add a per-column unique constraint | Yes |
| Remove a unique constraint | No |
| Rename a column | No |
| Change a column type | No |
| Change nullability | No |
| Change a default | No |
| Composite unique constraint or index | No |
| Foreign key | No |

For an unsupported change, plan a replacement column or table plus a controlled
data migration. Do not assume PATCH performs an in-place rename or cast.

## Generated SDK Row Operations

Create the table first, then regenerate the SDK:

```fish
npx poly generate
```

Use the generated path and methods:

| Operation | SDK method | REST fallback | Response |
| --- | --- | --- | --- |
| Insert | `insertMany` | `POST /tables/{id}/insert` | `results`, `pagination` |
| Select | `selectMany` | `POST /tables/{id}/select` | `results`, `pagination` |
| Count | `count` | `POST /tables/{id}/count` | `{ count }` |
| Upsert | `upsertMany` | `POST /tables/{id}/upsert` | `results`, `pagination` |
| Update | `updateMany` | `POST /tables/{id}/update` | `results`, `pagination` |
| Delete | `deleteMany` | `POST /tables/{id}/delete` | `{ deleted }` |

Prefer the generated SDK. Use REST only for an environment or language where a
generated Node/Python client is unavailable.

## TypeScript Example

Replace `customer.data.CustomerState` with the exact generated path:

```typescript
import { tabi } from "polyapi";

const customerState = tabi.customer.data.CustomerState;

await customerState.upsertMany({
  data: [
    {
      external_id: "cust_001",
      data_type: "company",
      json_data: { name: "Acme", region: "EMEA" },
    },
  ],
});

const page = await customerState.selectMany({
  where: { data_type: "company" },
  limit: 1000,
  offset: 0,
  orderBy: { id: "asc" },
});

for (const row of page.results) {
  // Process rows without logging unrestricted payloads.
  console.log(row.id, row.external_id);
}
```

Upsert conflict identity is limited to one unique column. Do not design an
upsert that depends on a combination of columns.

## Query Rules

- `where` supports top-level column filters and `AND`, `OR`, and `NOT` groups.
- Supported scalar operators include equality, comparisons, `in`, `notIn`,
  `contains`, `startsWith`, `endsWith`, and `not`; use generated types as the
  exact contract for a table and SDK version.
- `limit` is clamped to 1-1,000 rows. Use `offset` for subsequent pages.
- Every offset-paginated query needs deterministic `orderBy` on a stable unique
  column. `id` is the safest default.
- Current filters do not query inside `jsonb` objects. Promote every field that
  must be filtered or ordered to a top-level column.
- `updateMany` and `deleteMany` accept an omitted `where`, which affects every
  row. Treat an explicit, tested `where` as mandatory application policy.

## Lifecycle and Retention

Record the expected row growth, cleanup condition, retention period, and owner.
Use a PolyAPI job for scheduled cleanup or lifecycle transitions. Test cleanup
with the same narrow filters and cardinality checks used for production row
mutations.

## Current Sources of Truth

- Target environment Swagger and `/swagger-json` for accepted API fields.
- Generated project SDK for exact context paths, methods, and types.
- PolyAPI documentation: Tabi Tables, Row Operations, Best Practices, and
  Limitations.
