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

`jira-service/` — a real Jira Cloud REST API v3 adapter, not a mock. Needs
`JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, and `JIRA_PROJECT_KEY` set
in your own `.env` (see `.env.example`) — get a token at
https://id.atlassian.com/manage-profile/security/api-tokens. Without them,
`/health` still returns 200 (`jira: "unconfigured"`) rather than failing
the container, so the rest of the stack — and CI — isn't blocked on having
real Jira credentials.

| Route | Purpose |
|---|---|
| `GET /health` | Liveness — `jira: ok/degraded/unreachable/unconfigured` |
| `GET /issues` | List issues via JQL (`?project_key=`, defaults to `JIRA_PROJECT_KEY`) |
| `GET /issues/{key}` | Get one issue |
| `POST /issues` | Create an issue (`summary`, `description`, `issue_type`, `project_key`) |

Auth is a Jira API token over HTTP Basic — the simpler, working path.
The integrated-app-stack skill's longer-term guidance is to route real
domain-system credentials through Keycloak (layer 1) as an OIDC client
instead of static keys in env vars; that needs a 3LO OAuth app registered
in the Atlassian developer console with Keycloak configured as a broker,
which is a separate, heavier setup — worth doing before this goes past a
single developer's laptop.

`list_jira_issues`, `get_jira_issue`, and `create_jira_issue` are exposed
as Claude Code tools via `mcp-server` — see the orchestration skill.

Start: `docker compose --profile apps up -d`

All four services are built, scanned, and smoke-tested by the pipeline —
see `ci-cd/services.yaml` at the repo root.

See `.claude/skills/integrated-app-stack/SKILL.md` for implementation patterns.
