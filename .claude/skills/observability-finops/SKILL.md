---
name: observability-finops
description: Use when adding metrics, tracing, dashboards, or cost/token tracking for this architecture. Trigger on mentions of Prometheus, Grafana, OpenTelemetry, dashboards, token cost, or "observability layer."
---

# Layer 7 — Observability & FinOps

Open source equivalents of the deck's "Cloud/Token cost monitoring ·
Telemetry · Performance dashboards":

| Deck concept | Local implementation |
|---|---|
| Telemetry / performance dashboards | Prometheus (metrics) + Grafana (dashboards) |
| Distributed tracing | OpenTelemetry Collector, `otlp` in / `logging` + `prometheus` exporters out |
| Token/cost monitoring | Custom Prometheus counters in `agent-service` (see below) — no hosted LLM-observability SaaS is used, by design |

## Working in this layer

1. **Every service must expose `/health` and `/metrics`** (Prometheus
   format) — `agent-service` and the FastAPI services already do this via
   `prometheus_client`'s `make_asgi_app()`; follow the same pattern for any
   new service, and add it to `prometheus.yml`'s `scrape_configs`.
2. **Token/cost tracking**: since everything runs on local, free, open
   models, "cost" here means *compute* — track tokens generated and
   request latency per model as the FinOps proxy. Add a
   `Counter("llm_tokens_total", ["model"])` and increment it with
   Ollama's response `eval_count`/`prompt_eval_count` fields inside the
   `/chat` route in `agent-service/main.py`. If a future task adds a real
   hosted-provider fallback, track its actual dollar cost the same way,
   labeled by provider, so local vs. hosted spend is visible side by side.
3. **Dashboards**: add Grafana dashboard JSON under
   `layers/7-observability-finops/grafana-dashboards/` — they're
   auto-provisioned via the volume mount in `docker-compose.yml`. Build one
   dashboard per layer (agent latency, CRM request volume, token usage) so
   dashboards map onto the same 7-layer structure as the rest of the repo.
4. **Tracing**: instrument new agent workflows with
   `opentelemetry-sdk` spans (already a dependency) so multi-step chains/
   graphs/crews show up as traces, not just aggregate metrics — this
   matters most for LangGraph/CrewAI flows where a single request fans out
   into several LLM calls.

## Testing

- `curl http://localhost:9090/-/healthy` — Prometheus.
- `curl http://localhost:9090/api/v1/targets` — confirms all scrape
  targets are `up`.
- `http://localhost:3001` (admin/admin) — Grafana; confirm the Prometheus
  datasource and provisioned dashboards load.

## Gotchas

- Prometheus only scrapes targets already listed in `prometheus.yml` — a
  new service's `/metrics` endpoint being reachable isn't enough, add the
  scrape config too.
- Don't put token/request content into metric labels (high cardinality,
  and it leaks data into a system meant for aggregate numbers) — labels
  should be things like `model`, `endpoint`, `status`, not prompt text.
