---
name: orchestration
description: Use when wiring services together, adding a new tool that Claude Code should be able to call, changing service-to-service routing, or standing up Kubernetes locally. Trigger on mentions of MCP, A2A, Kubernetes, kind/k3d, microservices, API gateway, Traefik, or "orchestration layer."
---

# Layer 5 — Orchestration

Open source equivalents of the deck's "Kubernetes · MCP/A2A · Microservices
· APIs":

| Deck concept | Local implementation |
|---|---|
| MCP | `layers/5-orchestration/mcp-server` — the real Model Context Protocol, run with Python's `mcp` SDK, `streamable-http` transport, exposed on port 8003 |
| A2A (agent-to-agent) | Direct HTTP calls between agent-service/mcp-server/mock-crm-service over `sdlc-net`; formalize with a message bus (see Extending below) only if you need async/event-driven A2A |
| Microservices / APIs | Each layer's FastAPI service is its own microservice; Traefik is the gateway |
| Kubernetes | Not run by default (heavy for a laptop) — `kind` or `k3d` can stand up a real local cluster; see below |

This is the layer that makes the whole stack usable **from Claude Code
itself**, via MCP.

## Working in this layer

1. **Exposing a new capability to Claude Code**: add a new `@mcp.tool()`
   function in `mcp-server/server.py` that calls the relevant layer's HTTP
   API (mirror the existing `ask_local_llm`/`rag_query`/`list_customers`
   tools) — a short docstring is required, it becomes the tool description
   Claude Code sees. Keep tools narrow and named for what they do
   (`create_customer`, not `crm_action`).
2. **Registering the server with Claude Code**:
   ```bash
   claude mcp add sdlc-stack --transport http http://localhost:8003/mcp
   ```
   Re-run this after changing the server's tool list; restart the
   container (`docker compose restart mcp-server`) after editing
   `server.py`.
3. **Routing through Traefik**: label a new service with
   `traefik.enable=true` and a `traefik.http.routers.<name>.rule=Host(...)`
   label if you want it reachable through the gateway on port 80 instead of
   its raw port — most local dev doesn't need this, it matters once you're
   modeling real ingress/routing rules.
4. **Standing up real Kubernetes locally** (optional, only if a task
   specifically needs k8s manifests/Helm charts rather than compose):
   ```bash
   brew install kind kubectl helm
   kind create cluster --name sdlc-local
   ```
   Then translate the relevant compose services to manifests under
   `layers/5-orchestration/k8s/` — do this incrementally, only for
   services actually being tested against real k8s behavior (e.g. HPA,
   network policies), not as a wholesale compose replacement.

## Testing

- `curl http://localhost:8003/mcp` should respond (MCP protocol handshake,
  not a browsable page — a 4xx/5xx with a protocol-shaped body is normal
  for a bare GET; use the `claude mcp` CLI or an MCP inspector for a real
  check).
- From Claude Code, after registering: ask it to list available tools and
  confirm the ones you added appear.
- `curl http://localhost:8090` — Traefik dashboard, confirms routing rules.

## Gotchas

- `stateless_http=True` on `FastMCP` is required for this server to work
  behind a load balancer / restart cleanly — don't remove it.
- MCP tool docstrings are the *only* thing Claude Code sees to decide when
  to call a tool — vague docstrings get skipped or misused; be specific
  about what the tool does and what its arguments mean.
- If you add authentication to any downstream service (Keycloak-issued
  tokens from layer 1), the MCP server needs to acquire and forward that
  token — don't let it fall back to calling downstream services
  unauthenticated once auth exists anywhere in the chain.
