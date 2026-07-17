---
name: agentic-comms
description: Use when building or modifying human-facing chat/copilot interfaces for this architecture. Trigger on mentions of Open WebUI, chatbots, copilots, or "agentic comms layer."
---

# Layer 6 — Agentic Comms Layer

Open source equivalent of the deck's "CoPilots · ChatBots · Human-facing AI
interfaces":

| Deck concept | Local implementation |
|---|---|
| Human-facing chat UI | Open WebUI, at `localhost:3000`, talking to Ollama directly |
| CoPilot embedded in a workflow | Custom small frontend calling `agent-service` (layer 3) or `mcp-server` (layer 5) — build only when a task needs UI beyond Open WebUI's chat |

## Working in this layer

1. **Default chat UI**: Open WebUI needs no code changes to use — it's
   pre-wired to Ollama in `docker-compose.yml`. Point it at additional
   models by pulling them in the `ollama` container (see data-kx-backbone
   skill) — they appear in its model picker automatically.
2. **Connecting Open WebUI to RAG/agents instead of raw Ollama**: Open
   WebUI supports OpenAI-compatible custom endpoints in its admin settings
   — point it at `agent-service`'s `/chat` route only after adding an
   OpenAI-compatible wrapper route there (Open WebUI expects
   `/v1/chat/completions` shape, not this repo's simpler `/chat` shape) —
   add that adapter route in `agent-service/main.py` rather than modifying
   Open WebUI.
3. **Building a bespoke copilot UI** (e.g. embedded in a specific internal
   tool): create it under `layers/6-agentic-comms/<name>-ui/` as its own
   small app (a lightweight React/Vite app or server-rendered page is
   enough), calling `mcp-server` or `agent-service` over HTTP — never call
   Ollama or Qdrant directly from a UI layer, always go through layer 3 or
   5 so guardrails and observability stay in the loop.

## Testing

- Open `http://localhost:3000` in a browser, confirm a model is selectable
  and a message round-trips.
- For a custom copilot UI, add a route-level smoke test the same way as
  agent-service (see ai-agent-backbone skill).

## Gotchas

- Open WebUI stores its own user accounts/chat history in its container —
  don't treat it as stateless; back up its volume if conversation history
  matters.
- Don't give any human-facing UI direct network access to `postgres` or
  `qdrant` — route everything through an API layer so data access stays
  auditable from layer 7.
