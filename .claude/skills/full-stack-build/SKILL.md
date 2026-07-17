---
name: full-stack-build
description: Use this skill whenever standing up, rebuilding, or repairing the whole AI-native SDLC architecture from scratch — not just one layer. Trigger on requests like "build the whole stack", "rebuild the architecture", "start everything", "the containers won't build", or any task that spans more than one layer at once. This skill is the corrected, known-good build path — read it before touching docker-compose.yml or any requirements.txt.
---

# Full-stack build — corrected, known-good path

This skill exists because the first pass at this architecture hit a chain of
real dependency and transport bugs when actually built on a laptop. Every
fix below was discovered by building the stack for real, not guessed in
advance. Follow this skill instead of re-deriving package versions from
scratch — re-pinning old exact versions is what caused the failures the
first time.

## Build order (bottom to top — always in this order)

The 7 layers depend on each other upward, so bring them up in this order.
Each step should be verified working before moving to the next.

1. **Infrastructure** (Colima/Docker running, LocalStack + Keycloak if needed)
2. **Data / KX Backbone** (Ollama, Qdrant, Postgres, MinIO) — pull a model here
3. **AI / Agent Backbone** (agent-service) — needs layer 2 running to pass health checks
4. **Integrated App Stack** (mock-crm-service) — needs Postgres from layer 2
5. **Orchestration** (mcp-server, Traefik) — needs layers 3 and 4 running, since its tools call them
6. **Agentic Comms** (Open WebUI, or a custom UI) — needs layer 2 (Ollama) at minimum
7. **Observability & FinOps** (Prometheus, Grafana, OTel Collector) — can start any time, scrapes whatever is already up

Bringing up `orchestration` before `core` (layers 2-3) is a common mistake —
`mcp-server`'s tools will build and start fine, but every tool call fails
with a DNS resolution error because the services it points at don't exist
yet.

**Default to starting every service, every time** — this skill's job is to
stand up the *whole* architecture, not a partial slice. Always run:
```
docker compose --profile full up -d
```
This brings up all 14 services across all 7 layers in one shot (Compose
resolves the dependency graph internally, so `depends_on` ordering is
respected even though every profile is requested together). Only fall back
to a narrower profile combination (e.g. `--profile core --profile
orchestration --profile apps`) if the user explicitly asks for a partial
stack or flags a laptop RAM constraint — `--profile full` needs 16GB+ RAM
per the usage comment at the top of `docker-compose.yml`.

## The dependency-pinning lesson (read this before editing any requirements.txt)

**What went wrong originally**: `agent-service/requirements.txt` pinned exact
versions for `fastapi`, `langchain`, `crewai`, `httpx`, `pydantic`, and the
`opentelemetry-*` packages all at once. CrewAI's 1.x line pulls in a large,
fast-moving dependency tree (chromadb, lancedb, mcp, instructor) with its
own minimum-version requirements that outgrow hand-picked exact pins within
months. Every exact pin on a package CrewAI also depends on caused a new
`ResolutionImpossible` error — first on `langchain`, then `httpx`, then
`opentelemetry-api`, then `pydantic`, then `uvicorn`. Chasing these one at a
time is a trap: fixing one pin just surfaces the next one pip already knew
about.

**The fix**: only pin exact versions on packages CrewAI's tree never
touches. Leave everything CrewAI depends on unpinned (or minimum-only) so
pip resolves the whole graph in one pass instead of fighting it piece by piece.

**Known-good `layers/3-ai-agent-backbone/agent-service/requirements.txt`**:
```
fastapi
uvicorn[standard]
langchain
langchain-community
langgraph
crewai>=1.0.0,<2.0.0
pyautogen==0.2.35
qdrant-client
psycopg2-binary==2.9.9
pydantic
httpx
prometheus-client==0.20.0
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp
```
Only `pyautogen`, `psycopg2-binary`, and `prometheus-client` are exact-pinned
— none of the three are in CrewAI's dependency tree, so they're safe to hold
steady. Everything else is intentionally unpinned. If a future CrewAI
release introduces a new conflict, unpin whatever pip's error message names
next rather than re-pinning it to a specific number.

**Known-good `layers/5-orchestration/mcp-server/requirements.txt`**:
```
mcp>=1.10.0
httpx
prometheus-client==0.20.0
```
The original `mcp==1.2.0` pin predates the `streamable-http` transport this
server uses — that's a hard minimum, not a style preference.
`prometheus-client` backs the `/metrics` route added via FastMCP's
`custom_route` (see `server.py`) — same exact pin as `agent-service` and
`mock-crm-service` use, since none of the three are in CrewAI's dependency
tree and there's no reason for the pin to drift between services.

## The FastMCP transport bug (read this before touching server.py)

`FastMCP.run()` does **not** accept `host`/`port` keyword arguments — those
belong on the `FastMCP(...)` constructor. Passing them to `.run()` throws
`TypeError: FastMCP.run() got an unexpected keyword argument 'host'`. The
correct pattern, already in `layers/5-orchestration/mcp-server/server.py`:
```python
mcp = FastMCP("sdlc-stack", stateless_http=True, host="0.0.0.0", port=8003)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```
Do not move `host`/`port` back onto `.run()`.

A `curl http://localhost:8003/mcp` returning
`{"jsonrpc":"2.0","id":"server-error","error":{"code":-32600,"message":"Not
Acceptable: Client must accept text/event-stream"}}` is **success**, not a
bug — `curl` isn't sending the streaming headers a real MCP client sends.
Confirm the server is genuinely working via `claude mcp list` /
`/mcp` inside a Claude Code session, not via `curl`'s response body.

## Rebuilding after a requirements.txt change

Always rebuild the specific service, not the whole stack, to save time:
```
docker compose build agent-service
docker compose up -d agent-service
docker compose logs agent-service
```
Swap the service name for `mcp-server`, `mock-crm-service`, etc. as needed.
`docker compose --profile core --profile orchestration --profile apps up -d --build`
rebuilds everything that's changed, but is slower — use it after multiple
changes across services, not after every single edit.

## Verifying the full stack is actually healthy

`docker compose ps` only shows a container is running, not that it's
working. Use the endpoint checks below (also in `scripts/health-check.sh`):
```
curl http://localhost:11434/api/tags        # Ollama has models pulled
curl http://localhost:6333/collections      # Qdrant
curl http://localhost:8001/health           # agent-service can reach Ollama + Qdrant
curl http://localhost:8002/health           # mock-crm-service
curl http://localhost:8003/mcp              # mcp-server (see note above — an error body is fine)
curl http://localhost:3000                  # Open WebUI
```
Then confirm the MCP connection from Claude Code's side, not just the
server's side — run `/mcp` in a `claude` session (CLI) or check the
connectors indicator in Claude Code Desktop, and look for `sdlc-stack`
showing as connected, not failed.

## Registering with Claude Code (do this once per machine)

```
claude mcp add sdlc-stack --transport http http://localhost:8003/mcp
```
This writes to `~/.claude.json`, which both the CLI and the Claude Code
Desktop app's Code tab read — you do not need to register it separately in
each surface.
