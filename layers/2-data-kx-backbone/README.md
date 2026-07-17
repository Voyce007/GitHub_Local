# Layer 2 — Data / KX Backbone

Local open source equivalents of closed LLM/SLM, vector DB, structured +
unstructured stores, and guardrails.

| Service | Image | Port | Purpose |
|---|---|---|---|
| Ollama | `ollama/ollama` | 11434 | Local LLM/SLM runtime |
| Qdrant | `qdrant/qdrant` | 6333/6334 | Vector database |
| Postgres | `postgres:16-alpine` | 5432 | Structured store |
| MinIO | `minio/minio` | 9000/9001 | Unstructured / object store (S3-compatible) |

Start: `docker compose --profile data up -d`, then
`docker exec -it ollama-svc ollama pull llama3.1:8b` (or a smaller model —
see the skill for RAM sizing guidance).

Guardrails are implemented in-process inside `agent-service` (layer 3), not
as a separate service here.

See `.claude/skills/data-kx-backbone/SKILL.md` for implementation patterns.
