# Layer 3 — AI / Agent Backbone

FastAPI service (`agent-service/`) wrapping open source equivalents of
Claude Code / LangChain / AutoGen / Google ADK / CrewAI, all backed by the
local Ollama + Qdrant from layer 2.

| Route | Purpose |
|---|---|
| `GET /health` | Liveness + dependency checks |
| `POST /chat` | Single-turn LLM call |
| `POST /rag/query` | Retrieval-augmented query via Qdrant |
| `POST /agents/crew` | CrewAI multi-agent run (stub — extend per the skill) |
| `GET /metrics` | Prometheus metrics |

Start: `docker compose --profile agents up -d` (or `core`, which includes it).

See `.claude/skills/ai-agent-backbone/SKILL.md` for implementation patterns —
where to add LangChain chains, LangGraph graphs, CrewAI crews, and AutoGen
flows.
