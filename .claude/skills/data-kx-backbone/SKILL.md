---
name: data-kx-backbone
description: Use when working with local LLMs/SLMs, embeddings, vector search, structured or unstructured data storage, or guardrails for this architecture. Trigger on mentions of Ollama, Qdrant, embeddings, RAG ingestion, MinIO, Postgres schemas in the data layer, or "data backbone."
---

# Layer 2 — Data / KX Backbone

Open source local equivalents of the deck's "Closed LLM/SLM · Vector DB ·
Structured + Unstructured stores · Guardrails":

| Deck concept | Local implementation |
|---|---|
| Closed LLM/SLM | Ollama, serving open-weight models (llama3.1, mistral, phi3, qwen2.5, etc.) — "closed" in the deck means "not calling out to a third party," which a fully local model satisfies |
| Vector DB | Qdrant |
| Structured store | Postgres |
| Unstructured store | MinIO (S3-compatible object storage) |
| Guardrails | Guardrails-AI or NeMo Guardrails as a Python dependency inside the agent-service (layer 3), not a separate infra service |

## First-time setup

```bash
docker compose --profile data up -d
docker exec -it ollama-svc ollama pull llama3.1:8b   # or a smaller model — see sizing below
```

Model sizing for a MacBook Pro (unified memory is shared with everything
else running):
- 8GB RAM: `phi3:mini` or `qwen2.5:3b` only: everything else will thrash.
- 16GB RAM: `llama3.1:8b` or `mistral:7b` comfortably alongside `core` profile.
- 32GB+ RAM: `llama3.1:8b` plus `full` profile is fine; larger models (13B+) still tight.

## Working in this layer

1. **Ingesting documents for RAG**: chunk → embed → upsert into Qdrant. Use
   `langchain`'s text splitters for chunking (already a dependency of
   `agent-service`) and Ollama's `/api/embeddings` endpoint (or a dedicated
   embedding model like `nomic-embed-text`, pulled the same way as above)
   to generate vectors before upserting to Qdrant's `/collections/{name}/points`
   endpoint. Keep ingestion scripts in `layers/2-data-kx-backbone/ingest/`
   (create it) — one script per document source.
2. **Structured data**: use Postgres for anything relational — the
   integrated-app-stack layer's own schema lives in the same instance under
   a separate database/schema; keep layer boundaries by schema, not by
   spinning up a second Postgres unless you specifically need isolation.
3. **Unstructured data**: use MinIO via the standard S3 API/SDK (same
   pattern as LocalStack in layer 1 — code written against S3 works against
   both). Console at `localhost:9001`.
4. **Guardrails**: add input/output validation (PII detection, jailbreak
   detection, schema-constrained output) as a wrapper around calls in
   `agent-service`, not as a new network service — it should run in-process
   so it can't be bypassed by calling Ollama directly from another service.

## Testing

- `curl http://localhost:6333/collections` — Qdrant is up and lists
  collections.
- `curl http://localhost:11434/api/tags` — Ollama is up and lists pulled
  models.
- `curl http://localhost:9000/minio/health/live` — MinIO is up.

## Gotchas

- Ollama's first `ollama pull` for an 8B model downloads ~4.5GB — do this
  before you need it, not mid-task.
- Qdrant collections must be created with a matching vector dimension
  before upserting (e.g. 768 for `nomic-embed-text`, 4096 for some
  Llama-family embedding heads) — a dimension mismatch fails the upsert,
  it does not silently truncate.
- MinIO and LocalStack's S3 emulation can coexist, but pick one per use
  case: MinIO for "this is genuinely our unstructured store," LocalStack
  for "we're testing AWS-specific behavior."
