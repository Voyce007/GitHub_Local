# Layer 4 — Integrated App Stack

`mock-crm-service/` — a FastAPI service over Postgres, shaped like a real
CRM/ERP domain integration, meant to be extended or replaced with a real
system (Twenty CRM, EspoCRM, ERPNext are open source options) as needed.

| Route | Purpose |
|---|---|
| `GET /health` | Liveness |
| `GET /customers` | List customers |
| `POST /customers` | Create a customer |

`mock-erp-service/` — a FastAPI service over Postgres, shaped like a real
ERP domain integration (inventory + orders). Same pattern as the CRM
stub: extend it directly, or replace it with a real system (ERPNext).

| Route | Purpose |
|---|---|
| `GET /health` | Liveness |
| `GET /products` | List products and stock levels |
| `POST /products` | Create a product |
| `GET /orders` | List orders |
| `POST /orders` | Place an order (decrements stock; 409 if insufficient) |

`erp-ui/` — a browser UI for mock-erp-service (product/stock table,
order table, forms to add a product and place an order). A FastAPI app
that serves the page and proxies `/api/*` to `ERP_SERVICE_URL`
server-side, so the browser never talks to mock-erp-service directly
(no CORS, works the same via `localhost` or behind Traefik).

| Route | Purpose |
|---|---|
| `GET /` | The UI |
| `GET /health` | Liveness |
| `GET/POST /api/products` | Proxies to mock-erp-service `/products` |
| `GET/POST /api/orders` | Proxies to mock-erp-service `/orders` |

Open http://localhost:8005 once running.

Start: `docker compose --profile apps up -d`

All three services are built, scanned, and smoke-tested by the pipeline —
see `ci-cd/services.yaml` at the repo root.

See `.claude/skills/integrated-app-stack/SKILL.md` for implementation patterns.
