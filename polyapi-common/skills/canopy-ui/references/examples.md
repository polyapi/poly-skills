# Canopy UI — JSON Examples

## Minimal working skeleton

A complete, deployable application with one table-backed CRUD collection and one standalone form.

```jsonc
{
  "name": "My App",
  "subpath": "my-app",
  "icon": "https://example.com/logo.svg",
  "login": {
    "title": "My App Login",
    "logoSrc": "https://example.com/logo.svg",
    "allowPolyApiKey": true
  },
  "allowAppSwitcher": false,
  "allowEnvironmentSwitcher": false,

  "collections": [
    {
      "id": "orders",
      "name": "Orders",
      "group": "Operations",
      "nameProperty": "orderNumber",
      "properties": {
        "id":          { "label": "ID",           "type": "text",   "readOnly": true,
                         "excludeFromCreate": true, "excludeFromUpdate": true },
        "orderNumber": { "label": "Order Number", "type": "text" },
        "status":      { "label": "Status",       "type": "enum",
                         "values": [{ "name": "Open", "value": "OPEN" },
                                    { "name": "Closed", "value": "CLOSED" }] },
        "amount":      { "label": "Amount",       "type": "number", "step": 0.01 }
      },
      "itemActions": ["get", "update"],
      "list": {
        "paginated": true,
        "function": {
          "path": "myapp.ordersDb",
          "type": "query",
          "operation": "select",
          "arguments": {
            "orderBy": { "value": { "orderNumber": "asc" } },
            "limit": { "value": 1000 }
          }
        }
      },
      "get": {
        "function": {
          "path": "myapp.ordersDb",
          "type": "query",
          "operation": "select",
          "arguments": {
            "where": { "value": { "id": { "id": true } } }
          }
        }
      },
      "create": {
        "actionLabel": "New Order",
        "function": {
          "path": "myapp.ordersDb",
          "type": "query",
          "operation": "insert",
          "arguments": { "data": { "data": true } }
        },
        "submitMode": "all"
      },
      "update": {
        "submitMode": "changed",
        "function": {
          "path": "myapp.ordersDb",
          "type": "query",
          "operation": "update",
          "arguments": {
            "where": { "value": { "id": { "id": true } } },
            "data": { "data": true }
          }
        }
      },
      "delete": {
        "confirmTitle": "Delete order?",
        "confirmText": "This cannot be undone.",
        "function": {
          "path": "myapp.ordersDb",
          "type": "query",
          "operation": "delete",
          "arguments": {
            "where": { "value": { "id": { "id": true } } }
          }
        }
      }
    }
  ],

  "forms": [
    {
      "title": "Send Confirmation",
      "subpath": "send-confirmation",
      "showSidebar": false,
      "showHeader": false,
      "cancel": false,
      "prepare": {
        "function": {
          "path": "myapp.orders.getById",
          "type": "server",
          "arguments": { "id": { "queryParam": { "key": "orderId", "type": "text" } } }
        }
      },
      "properties": {
        "orderNumber": { "label": "Order Number", "type": "text", "readOnly": true },
        "email":       { "label": "Recipient Email", "type": "text", "required": true }
      },
      "submit": {
        "label": "Send",
        "icon": "send",
        "variant": "primary",
        "location": "bottom",
        "function": {
          "path": "myapp.orders.sendConfirmation",
          "type": "server",
          "arguments": {
            "orderId": { "queryParam": { "key": "orderId", "type": "text" } },
            "email":   { "data": "email" }
          }
        }
      },
      "response": {
        "type": "confirmation",
        "confirmation": { "title": "Done", "message": "Confirmation sent successfully." }
      }
    }
  ]
}
```

---

## CRUD collection (tasks)

```jsonc
{
  "id": "tasks", "name": "Tasks", "group": "Dashboard",
  "nameProperty": "title",
  "properties": {
    "id":     { "label": "ID", "readOnly": true,
                "excludeFromCreate": true, "excludeFromUpdate": true },
    "title":  { "label": "Title", "type": "text" },
    "status": { "label": "Status", "type": "enum",
                "values": [{ "name": "To Do", "value": "TODO" }] }
  },
  "itemActions": ["get", "update"],
  "list": {
    "function": { "path": "dashboard.tasksDb", "type": "query", "operation": "select",
                  "arguments": { "limit": { "value": 1000 } } },
    "propertyMapping": { "id": "id", "name": "title", "description": "status" },
    "paginated": true
  },
  "get": {
    "function": { "path": "dashboard.tasksDb", "type": "query", "operation": "select",
                  "arguments": { "where": { "value": { "id": { "id": true } } } } }
  },
  "create": {
    "actionLabel": "Add", "submitLabel": "Save",
    "function": { "path": "dashboard.tasksDb", "type": "query", "operation": "insert",
                  "arguments": { "data": { "data": true } } },
    "submitMode": "all"
  },
  "update": {
    "function": { "path": "dashboard.tasksDb", "type": "query", "operation": "update",
                  "arguments": { "where": { "value": { "id": { "id": true } } },
                                 "data": { "data": true } } },
    "submitMode": "changed"
  },
  "delete": {
    "confirmTitle": "Delete task?", "confirmText": "This cannot be undone.",
    "function": { "path": "dashboard.tasksDb", "type": "query", "operation": "delete",
                  "arguments": { "where": { "value": { "id": { "id": true } } } } }
  }
}
```

---

## Standalone form with prepare

```jsonc
{
  "title": "Card Payment",
  "subpath": "card-payment",
  "properties": {
    "cardNumber": { "label": "Card", "type": "text" },
    "reservationBalance": { "label": "Balance", "type": "text", "readOnly": true }
  },
  "prepare": {
    "function": {
      "path": "myapp.payments.fetchBalance",
      "type": "server",
      "arguments": { "reservationId": { "queryParam": { "key": "reservationId", "type": "text" } } }
    }
  },
  "submit": {
    "function": { "path": "myapp.payments.applyPayment", "type": "server",
                  "arguments": { "body": { "data": true } } }
  },
  "response": {
    "type": "confirmation",
    "confirmation": { "title": "Applied" },
    "redirect": "/forms/card-payment?reservationId={{data.reservationId}}"
  }
}
```

---

## Multi-submit form

```jsonc
"submit": [
  { "label": "Save Draft",
    "submitMode": "filled",
    "function": { "path": "myapp.orders.saveDraft", "type": "server" } },
  { "label": "Submit Order",
    "confirm": { "title": "Submit?", "text": "This sends the order.", "variant": "primary" },
    "function": { "path": "myapp.orders.submit", "type": "server" },
    "response": { "type": "toast",
                  "toast": { "title": "Order submitted" },
                  "redirect": "/{{appId}}/collections/orders/{{data.id}}" } }
]
```

---

## Search → results → detail

```jsonc
{
  "id": "books",
  "name": "Books",
  "properties": {
    "search":  { "label": "Search",  "type": "text",      "queryParam": "q", "excludeFromDetail": true },
    "title":   { "label": "Title",   "type": "text" },
    "author":  { "label": "Author",  "type": "text" },
    "summary": { "label": "Summary", "type": "multiline" }
  },
  "itemActions": ["get"],
  "list": {
    "function": {
      "path": "library.books.search",
      "type": "server",
      "arguments": { "query": { "queryParam": { "key": "q", "type": "text" } } }
    },
    "propertyMapping": { "id": "id", "name": "title", "description": "author" }
  },
  "get": {
    "function": {
      "path": "library.books.getById",
      "type": "server",
      "arguments": { "id": { "id": true } }
    }
  }
}
```

---

## Filter controls — paginated list with dropdown and text search

```jsonc
"list": {
  "paginated": true,
  "function": {
    "path": "myapp.records.list",
    "type": "server",
    "arguments": {
      "hotelId": {
        "queryParam": {
          "key": "hotelid",
          "type": "enum",
          "label": "Hotel",
          "functionValues": {
            "valueKey": "value",
            "nameKey": "label",
            "function": { "path": "myapp.hotels.list", "type": "server" }
          }
        }
      },
      "status": {
        "queryParam": {
          "key": "filter",
          "type": "enum",
          "label": "Status",
          "allowEmpty": false,
          "defaultValue": "ACTIVE",
          "values": [
            { "name": "Active",   "value": "ACTIVE" },
            { "name": "Archived", "value": "ARCHIVED" }
          ]
        }
      },
      "search": {
        "queryParam": {
          "key": "search",
          "type": "text",
          "label": "Search",
          "allowEmpty": false,
          "defaultValue": ""
        }
      },
      "page": {
        "queryParam": "page",
        "fallback": { "data": 1 }
      }
    }
  }
}
```

---

## Tabi CRUD — query function argument patterns

```jsonc
"list": {
  "paginated": true,
  "function": {
    "type": "query",
    "path": "<context>.<tableName>",
    "operation": "select",
    "arguments": {
      "limit": { "value": 1000 },
      "orderBy": { "value": { "<displayOrDateField>": "asc" } }
    }
  }
}
```

```jsonc
"get": {
  "function": {
    "type": "query",
    "path": "<context>.<tableName>",
    "operation": "select",
    "arguments": {
      "where": { "value": { "<primaryKey>": { "id": true } } }
    }
  }
}
```

```jsonc
"create": {
  "submitMode": "all",
  "function": {
    "type": "query",
    "path": "<context>.<tableName>",
    "operation": "insert",
    "arguments": {
      "data": { "data": true }
    }
  }
}
```

```jsonc
"update": {
  "submitMode": "changed",
  "function": {
    "type": "query",
    "path": "<context>.<tableName>",
    "operation": "update",
    "arguments": {
      "data": { "data": true },
      "where": { "value": { "<primaryKey>": { "id": true } } }
    }
  }
}
```

```jsonc
"delete": {
  "function": {
    "type": "query",
    "path": "<context>.<tableName>",
    "operation": "delete",
    "arguments": {
      "where": { "value": { "<primaryKey>": { "id": true } } }
    }
  }
}
```
