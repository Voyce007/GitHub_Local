"""
Orchestration (Layer 5)
─────────────────────────
This is the piece that plugs the whole stack into Claude Code. It runs an
MCP (Model Context Protocol) server — the open, real implementation of the
deck's "MCP/A2A" box — and exposes the Agent Backbone (layer 3) and the
Integrated App Stack (layer 4) as tools. Kubernetes/microservices/APIs are
represented by docker-compose + this FastAPI-adjacent MCP server + Traefik
as the API gateway; swap in kind/k3d if you want a real local k8s cluster
(see layer README).

Register this server in Claude Code with:
    claude mcp add sdlc-stack --transport http http://localhost:8003/mcp
"""
import os
import httpx
from mcp.server.fastmcp import FastMCP
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://agent-service:8001")
CRM_SERVICE_URL = os.getenv("CRM_SERVICE_URL", "http://mock-crm-service:8002")

mcp = FastMCP("sdlc-stack", stateless_http=True, host="0.0.0.0", port=8003)

TOOL_CALLS = Counter("mcp_tool_calls_total", "Total tool calls", ["tool"])


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> Response:
    return PlainTextResponse("ok")


@mcp.custom_route("/metrics", methods=["GET"])
async def metrics(request: Request) -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@mcp.tool()
async def ask_local_llm(prompt: str, model: str = "llama3.1:8b") -> str:
    """Send a prompt to the local LLM (Ollama, via the Agent Backbone) and return the text response."""
    TOOL_CALLS.labels(tool="ask_local_llm").inc()
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{AGENT_SERVICE_URL}/chat", json={"prompt": prompt, "model": model})
        r.raise_for_status()
        return r.json().get("response", "")


@mcp.tool()
async def rag_query(query: str, collection: str = "default", top_k: int = 5) -> str:
    """Run a retrieval-augmented query against the local Qdrant vector store + local LLM."""
    TOOL_CALLS.labels(tool="rag_query").inc()
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            f"{AGENT_SERVICE_URL}/rag/query",
            json={"query": query, "collection": collection, "top_k": top_k},
        )
        r.raise_for_status()
        return r.json().get("response", "")


@mcp.tool()
async def list_customers() -> list:
    """List customers from the domain integration stub (stand-in for a real CRM/ERP)."""
    TOOL_CALLS.labels(tool="list_customers").inc()
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{CRM_SERVICE_URL}/customers")
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def create_customer(name: str, email: str) -> dict:
    """Create a customer record via the domain integration stub."""
    TOOL_CALLS.labels(tool="create_customer").inc()
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{CRM_SERVICE_URL}/customers", json={"name": name, "email": email})
        r.raise_for_status()
        return r.json()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
