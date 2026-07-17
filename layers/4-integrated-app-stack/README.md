# Layer 4 — Integrated App Stack

`mock-crm-service/` — a FastAPI service over Postgres, shaped like a real
CRM/ERP domain integration, meant to be extended or replaced with a real
system (Twenty CRM, EspoCRM, ERPNext are open source options) as needed.

| Route | Purpose |
|---|---|
| `GET /health` | Liveness |
| `GET /customers` | List customers |
| `POST /customers` | Create a customer |

Start: `docker compose --profile apps up -d`

See `.claude/skills/integrated-app-stack/SKILL.md` for implementation patterns.
