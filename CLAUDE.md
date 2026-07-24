# AI-Native SDLC Reference Architecture — working notes for Claude Code

This repo is a fully open source, laptop-deployable implementation of the
7-layer reference architecture below. Every proprietary/hosted element from
the original diagram has an open source local equivalent so the whole thing
runs on a MacBook Pro via Docker.

```
7  Observability & FinOps     Prometheus · Grafana · OpenTelemetry Collector
6  Agentic Comms Layer        Open WebUI (chat UI over local LLMs)
5  Orchestration               docker-compose (+ optional kind/k3d) · MCP server · Traefik
4  Integrated App Stack        FastAPI domain-integration stub (CRM-shaped) + Postgres
3  AI / Agent Backbone         LangChain · LangGraph · CrewAI · AutoGen, served via FastAPI
2  Data / KX Backbone          Ollama (local LLM/SLM) · Qdrant (vector DB) · Postgres · MinIO
1  Infrastructure               Docker/Colima (compute) · LocalStack (AWS emulation) · Keycloak (IAM)
```

## Before touching more than one layer

Read `.claude/skills/full-stack-build/SKILL.md` first. It documents the
correct bottom-to-top build/startup order, the known-good (already
conflict-resolved) `requirements.txt` contents for `agent-service` and
`mcp-server`, and the FastMCP `host`/`port` constructor-vs-`.run()` bug —
all discovered by actually building this stack, not guessed in advance.
Re-deriving package pins from scratch reintroduces bugs already fixed once.

For a plain-text, non-technical-reader install walkthrough (useful for
onboarding someone else, or a clean-machine rebuild), see `INSTALL.txt` at
the project root.

## How to work in this repo

- Each layer lives under `layers/<n>-<name>/` with its own README.
- Each layer has a matching skill at `.claude/skills/<name>/SKILL.md` — **read
  the relevant skill before making changes in that layer.** The skills encode
  the conventions (port numbers, env vars, service-to-service auth, testing
  pattern) that keep the layers interoperable.
- Services talk to each other over the `sdlc-net` docker network using their
  compose service names as hostnames (e.g. `http://agent-service:8001`), not
  `localhost`. From the host machine (your terminal, browser, or Claude Code
  itself) use `localhost:<port>`.
- `docker-compose.yml` uses profiles (`core`, `data`, `agents`, `apps`,
  `orchestration`, `comms`, `observability`, `infrastructure`, `full`) so you
  only run what a given task needs — check laptop RAM before adding `full`.
- The MCP server in `layers/5-orchestration/mcp-server` is what connects this
  whole stack back into Claude Code as tools. It's registered via the
  project-level `.mcp.json` (`http://localhost:8003/mcp`), so once it's
  running, Claude Code picks it up automatically (approve the one-time trust
  prompt) and you can drive the local LLM, vector search, and the CRM/ERP/
  Jira stubs directly from a Claude Code conversation.

## Implementation conventions

- **New service in an existing layer**: add it to `docker-compose.yml` under
  that layer's section, tag it with the layer's profile, add it to
  `prometheus.yml` scrape targets if it exposes metrics, and document the
  endpoint in the layer README.
- **New layer capability that needs a new open source tool**: prefer a tool
  with an official Docker image over a from-scratch build; note the license
  in the layer README (this repo is open-source-only, no proprietary SaaS
  dependencies, by design).
- **Env vars, not hardcoded URLs**: every cross-service call reads its target
  URL from an environment variable set in `docker-compose.yml`, so the same
  code works whether a dependency is local, swapped for a managed cloud
  service later, or pointed at a different profile.
- **Every service exposes `GET /health`** and, where practical, `/metrics`
  in Prometheus format — this is what layer 7 depends on.

## Common tasks

| Task | Where to look |
|---|---|
| Add a new agent workflow / chain / crew | `layers/3-ai-agent-backbone/agent-service`, skill: `ai-agent-backbone` |
| Add a new domain integration (real CRM/ERP) | `layers/4-integrated-app-stack`, skill: `integrated-app-stack` |
| Expose a new capability to Claude Code as an MCP tool | `layers/5-orchestration/mcp-server`, skill: `orchestration` |
| Add a chat/copilot surface | `layers/6-agentic-comms`, skill: `agentic-comms` |
| Add a dashboard or cost metric | `layers/7-observability-finops`, skill: `observability-finops` |
| Ingest documents into the vector store | `layers/2-data-kx-backbone`, skill: `data-kx-backbone` |
| Emulate a new AWS service, or add an IAM realm | `layers/1-infrastructure`, skill: `infrastructure-layer` |
| Add/remove a service from CI/CD (build, scan, smoke-test, release) | `ci-cd/services.yaml`, skill: `ci-cd` — the pipeline logic itself lives in the separate `cicd-tooling-architecture` repo, not here |

See `README.md` for first-time Mac setup.

## Source control / CI status

This repo is pushed to `github.com/Voyce007/GitHub_Local` (public, `main`
branch). `.github/workflows/ci.yml` and `release.yml` call reusable
workflows from `Voyce007/cicd-tooling-architecture@v1`. That tooling repo
now exists (created 2026-07-17, `ci.yml`/`release.yml` present, tagged
`v1`) and CI has been passing on `main` since 2026-07-20 — if a run fails,
treat it as a real failure in this repo's code or `ci-cd/services.yaml`,
not a missing-tooling-repo problem.
