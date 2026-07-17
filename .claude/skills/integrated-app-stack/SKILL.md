---
name: integrated-app-stack
description: Use when integrating business systems (CRM, ERP, or other domain applications) into this architecture, or extending the domain-integration stub. Trigger on mentions of mock-crm-service, CRM, ERP, domain integrations, or "integrated app stack."
---

# Layer 4 — Integrated App Stack

Open source equivalents of the deck's "Business capabilities (CRM, ERP,
etc.) — domain integrations":

| Deck concept | Local implementation |
|---|---|
| Domain integration pattern | `layers/4-integrated-app-stack/mock-crm-service` — a FastAPI service over its own Postgres tables, shaped like a real integration |
| Real CRM (optional, heavier) | Twenty CRM or EspoCRM (add as a new compose service if you want the genuine article, not just the stub) |
| Real ERP (optional, heavier) | ERPNext |

## Working in this layer

1. **Extending the stub**: the stub in `mock-crm-service/main.py` is meant
   to be edited directly, not treated as fixed scaffolding — add tables,
   routes, and validation as new business capabilities are needed. Keep
   each domain entity's routes together (e.g. all `customers` routes, then
   all `orders` routes) rather than one giant router file once it grows.
2. **Swapping in a real system**: when a real CRM/ERP is available, add it
   as its own compose service under the `apps` profile and put a thin
   adapter service in front of it that exposes the *same* route shapes
   agent-service and mcp-server already expect (`/customers`,
   `/customers` POST, etc.) — this way layers 3/5/6 don't need to change,
   only the adapter's internals do.
3. **Auth to real domain systems**: route real CRM/ERP credentials through
   Keycloak (layer 1) as an OIDC client, not as static API keys baked into
   this layer's env vars.

## Testing

- `curl http://localhost:8002/health`
- `curl http://localhost:8002/customers`
- `curl -X POST localhost:8002/customers -d '{"name":"Ada","email":"ada@example.com"}' -H 'content-type: application/json'`

## Gotchas

- The stub shares the `postgres` instance with other layers — use a
  distinct table/schema naming convention (it currently uses a bare
  `customers` table; prefix new tables, e.g. `crm_orders`, `crm_contacts`,
  as the schema grows) so collisions don't happen as other layers add
  their own tables.
- Don't let agent-service (layer 3) talk to Postgres directly for domain
  data — route it through this layer's API so business logic and
  validation stay in one place.
