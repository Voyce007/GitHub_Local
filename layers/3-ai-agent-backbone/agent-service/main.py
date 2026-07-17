"""
AI / Agent Backbone (Layer 3)
─────────────────────────────
Open source stand-in for: Claude Code (dev-time) · LangChain · AutoGen · CrewAI
Google ADK has no open source release, so it is intentionally not reproduced;
LangGraph fills the equivalent "structured multi-step agent graph" role.

Endpoints:
  GET  /health           liveness + dependency checks
  POST /chat              single-turn LLM call via Ollama
  POST /rag/query         retrieval-augmented answer using Qdrant
  POST /agents/crew       CrewAI multi-agent task run
  GET  /metrics           Prometheus metrics
"""
import os
from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, make_asgi_app
import httpx

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.1:8b")

app = FastAPI(title="AI / Agent Backbone", version="0.1.0")
app.mount("/metrics", make_asgi_app())

REQUEST_COUNT = Counter("agent_requests_total", "Total requests", ["endpoint"])
REQUEST_LATENCY = Histogram("agent_request_latency_seconds", "Latency", ["endpoint"])


class ChatRequest(BaseModel):
    prompt: str
    model: str = DEFAULT_MODEL


class RagRequest(BaseModel):
    query: str
    collection: str = "default"
    top_k: int = 5


@app.get("/health")
async def health():
    status = {"service": "ok"}
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            status["ollama"] = "ok" if r.status_code == 200 else "degraded"
        except Exception:
            status["ollama"] = "unreachable"
        try:
            r = await client.get(f"{QDRANT_URL}/readyz")
            status["qdrant"] = "ok" if r.status_code == 200 else "degraded"
        except Exception:
            status["qdrant"] = "unreachable"
    return status


@app.post("/chat")
async def chat(req: ChatRequest):
    REQUEST_COUNT.labels(endpoint="/chat").inc()
    with REQUEST_LATENCY.labels(endpoint="/chat").time():
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": req.model, "prompt": req.prompt, "stream": False},
            )
            resp.raise_for_status()
            return resp.json()


@app.post("/rag/query")
async def rag_query(req: RagRequest):
    """
    Minimal RAG loop: embed query -> search Qdrant -> stuff context -> ask Ollama.
    Swap in langchain's retrievers/chains here once you have real documents indexed
    (see layers/2-data-kx-backbone for the ingestion pattern).
    """
    REQUEST_COUNT.labels(endpoint="/rag/query").inc()
    async with httpx.AsyncClient(timeout=60) as client:
        search = await client.post(
            f"{QDRANT_URL}/collections/{req.collection}/points/search",
            json={"vector": [], "limit": req.top_k, "with_payload": True},
        )
        context_hits = search.json() if search.status_code == 200 else {"result": []}

    context_text = "\n".join(
        str(hit.get("payload", {})) for hit in context_hits.get("result", [])
    )
    prompt = f"Context:\n{context_text}\n\nQuestion: {req.query}\nAnswer:"
    return await chat(ChatRequest(prompt=prompt))


@app.post("/agents/crew")
async def run_crew(task: str):
    """
    Placeholder wiring for a CrewAI multi-agent run pointed at the local Ollama
    model instead of a hosted API. Extend this with real Agents/Tasks/Crew
    objects — see layers/3-ai-agent-backbone/README.md for the pattern Claude
    Code should follow when implementing new agent workflows.
    """
    return {
        "task": task,
        "status": "stub",
        "note": "Implement CrewAI Agents/Tasks here — see layer README.",
    }
