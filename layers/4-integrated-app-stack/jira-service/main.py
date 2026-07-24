"""
Integrated App Stack (Layer 4)
────────────────────────────────
Thin adapter in front of the real Jira Cloud REST API (v3) — unlike
mock-crm-service/mock-erp-service, this isn't a stub with its own Postgres
tables; it's a genuine domain-system connector. Exposes a small, stable
route shape (/issues, /issues/{key}) so agent-service and mcp-server don't
need to know anything about Jira's own API shape.

Auth: Jira Cloud API tokens over HTTP Basic (email + token). The
integrated-app-stack skill's long-term guidance is to route real domain-
system credentials through Keycloak (layer 1) as an OIDC client rather
than static keys in env vars — that requires registering a 3LO OAuth app
in the Atlassian developer console and configuring Keycloak as a broker,
which is a separate, heavier setup. This starts with the simpler, working
token-auth path; see the layer README for the OIDC hardening note.
"""
import os

import httpx
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, make_asgi_app
from pydantic import BaseModel

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "")

app = FastAPI(title="Integrated App Stack — Jira", version="0.1.0")
app.mount("/metrics", make_asgi_app())

REQUEST_COUNT = Counter("jira_requests_total", "Total requests", ["endpoint"])


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=JIRA_BASE_URL,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=15,
    )


class IssueCreate(BaseModel):
    summary: str
    description: str = ""
    issue_type: str = "Task"
    project_key: str = ""


@app.get("/health")
async def health():
    status = {"service": "ok"}
    if not (JIRA_BASE_URL and JIRA_EMAIL and JIRA_API_TOKEN):
        status["jira"] = "unconfigured"
        return status
    try:
        async with _client() as client:
            r = await client.get("/rest/api/3/myself")
            status["jira"] = "ok" if r.status_code == 200 else "degraded"
    except Exception:
        status["jira"] = "unreachable"
    return status


@app.get("/issues")
async def list_issues(project_key: str = "", max_results: int = 25):
    """List issues via JQL, defaulting to JIRA_PROJECT_KEY if no project_key is given."""
    REQUEST_COUNT.labels(endpoint="/issues").inc()
    key = project_key or JIRA_PROJECT_KEY
    if not key:
        raise HTTPException(status_code=400, detail="no project_key given and JIRA_PROJECT_KEY is unset")
    async with _client() as client:
        r = await client.get(
            "/rest/api/3/search",
            params={"jql": f"project={key} ORDER BY created DESC", "maxResults": max_results},
        )
        r.raise_for_status()
        data = r.json()
        return [
            {
                "key": issue["key"],
                "summary": issue["fields"]["summary"],
                "status": issue["fields"]["status"]["name"],
            }
            for issue in data.get("issues", [])
        ]


@app.get("/issues/{issue_key}")
async def get_issue(issue_key: str):
    REQUEST_COUNT.labels(endpoint="/issues/{key}").inc()
    async with _client() as client:
        r = await client.get(f"/rest/api/3/issue/{issue_key}")
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail=f"no issue {issue_key!r}")
        r.raise_for_status()
        data = r.json()
        return {
            "key": data["key"],
            "summary": data["fields"]["summary"],
            "status": data["fields"]["status"]["name"],
            "description": data["fields"].get("description"),
        }


@app.post("/issues")
async def create_issue(issue: IssueCreate):
    REQUEST_COUNT.labels(endpoint="/issues").inc()
    key = issue.project_key or JIRA_PROJECT_KEY
    if not key:
        raise HTTPException(status_code=400, detail="no project_key given and JIRA_PROJECT_KEY is unset")
    async with _client() as client:
        r = await client.post(
            "/rest/api/3/issue",
            json={
                "fields": {
                    "project": {"key": key},
                    "summary": issue.summary,
                    "issuetype": {"name": issue.issue_type},
                    **(
                        {
                            "description": {
                                "type": "doc",
                                "version": 1,
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": issue.description}],
                                    }
                                ],
                            }
                        }
                        if issue.description
                        else {}
                    ),
                }
            },
        )
        r.raise_for_status()
        data = r.json()
        return {"key": data["key"], "summary": issue.summary}
