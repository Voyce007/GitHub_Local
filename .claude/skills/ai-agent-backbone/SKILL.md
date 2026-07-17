---
name: ai-agent-backbone
description: Use when building or modifying agent logic, chains, multi-agent crews, or LLM-calling code for this architecture. Trigger on mentions of LangChain, LangGraph, CrewAI, AutoGen, agent-service, prompts, chains, or "agent backbone."
---

# Layer 3 — AI / Agent Backbone

Open source equivalents of the deck's "Claude Code · LangChain · AutoGen ·
Google ADK · CrewAI":

| Deck concept | Local implementation |
|---|---|
| Claude Code | Used as-is, dev-time — it's already open to any architecture and is how you're implementing this repo |
| LangChain | `langchain` / `langchain-community` — single-chain, retrieval, and tool-calling logic |
| AutoGen | `pyautogen` — conversational multi-agent patterns |
| CrewAI | `crewai` — role-based multi-agent orchestration |
| Google ADK | No open source release exists; `langgraph` fills the same "structured agent graph with explicit state" niche and is used here instead |

All of this lives in `layers/3-ai-agent-backbone/agent-service`, a FastAPI
app that talks to Ollama (layer 2) and Qdrant (layer 2), and is in turn
called by the MCP server (layer 5).

## Working in this layer

1. **Single-turn or tool-calling logic** → LangChain. Build chains in a new
   module under `agent-service/chains/`, and expose them via a new FastAPI
   route in `main.py` that calls the chain and returns its output — follow
   the existing `/chat` and `/rag/query` routes as the pattern (Prometheus
   counters + histogram, async httpx calls, env-var-configured URLs).
2. **Multi-step agent workflows with explicit state/branching** → LangGraph.
   Model the graph's nodes as functions in `agent-service/graphs/`, compile
   the graph once at module load, and expose a route that invokes it.
3. **Role-based multi-agent collaboration** (e.g. "researcher agent hands
   off to writer agent") → CrewAI. Define Agents/Tasks/Crew in
   `agent-service/crews/`, and wire them into the `/agents/crew` stub in
   `main.py`, replacing the placeholder.
4. **Conversational multi-agent patterns with human-in-the-loop** →
   AutoGen. Use its `GroupChat`/`ConversableAgent` primitives in
   `agent-service/autogen_flows/`.
5. **All of the above must point at Ollama, not a hosted API**, via
   `OLLAMA_BASE_URL` — LangChain's `ChatOllama`, CrewAI's LLM config, and
   AutoGen's `config_list` all support an OpenAI-compatible local endpoint;
   Ollama exposes one at `/v1`. Never hardcode a hosted-provider API key
   into this layer — the whole point of this stack is it runs fully local.

## Testing

- `curl http://localhost:8001/health` — reports whether the service can
  reach Ollama and Qdrant.
- `curl -X POST localhost:8001/chat -d '{"prompt":"hello"}' -H 'content-type: application/json'`
- After adding a new chain/graph/crew, add a smoke test under
  `agent-service/tests/` that calls the route with a fixed prompt and
  asserts a 200 + non-empty response — LLM output itself is non-deterministic,
  so assert shape/status, not exact text.

## Gotchas

- CrewAI and AutoGen both default to expecting an OpenAI API key at import
  time in older versions — pin the versions in `requirements.txt` (already
  done) and set a dummy `OPENAI_API_KEY=not-needed` env var if a library
  complains despite being pointed at Ollama.
- Keep prompts and few-shot examples in version-controlled files (e.g.
  `agent-service/prompts/*.txt`), not inline strings, so they can be
  iterated on without touching route logic.
- Small local models (3B–8B) follow tool-calling and JSON-schema
  instructions less reliably than large hosted models — add explicit
  output validation (see the Guardrails note in the data-kx-backbone skill)
  rather than assuming well-formed output.
