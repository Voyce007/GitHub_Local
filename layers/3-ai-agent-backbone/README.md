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

## Ontology discovery kit

`ontology-discovery-kit/` is a self-contained, exportable set of
collaborating agents that reverse-engineers an evidence-graded as-is
ontology from documentation extracts and example code, following the
Enterprise Ontology Design & Delivery Playbook. It contains:
- BA, EA, DA and Engineering persona subagents, plus an Ontology Steward and a Conformance agent
- a deterministic `ontokit` pipeline (validate, reconcile, grade, gates, unknowns, publish)
- a human approval gate
- a sample evidence batch.

It runs on Python and PyYAML only; it doesn't need the Docker stack. See its
`README.md`, `CLAUDE.md` and `docs/storyboard.html`.
Licence: repo licence. Dependencies are open source (PyYAML, MIT).
