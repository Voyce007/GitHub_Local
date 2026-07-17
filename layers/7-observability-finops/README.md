# Layer 7 — Observability & FinOps

Prometheus + Grafana + OpenTelemetry Collector. Token/compute-cost tracking
is implemented as custom Prometheus counters in `agent-service` (layer 3)
rather than a hosted LLM-observability SaaS.

Start: `docker compose --profile observability up -d`

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001` (admin/admin)
- OTel Collector OTLP endpoints: `4317` (gRPC) / `4318` (HTTP)

See `.claude/skills/observability-finops/SKILL.md` for implementation patterns.
