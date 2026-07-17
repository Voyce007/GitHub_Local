"""
Integrated App Stack (Layer 4)
────────────────────────────────
Stands in for real business capabilities (CRM, ERP, etc). Deliberately shaped
like a real domain integration — a REST API in front of its own Postgres
schema — so Claude Code can later swap this for a real CRM/ERP connector
(e.g. a Salesforce or SAP adapter) without changing how layers 3/5/6 talk
to it. Open source real-CRM options if you want the genuine article
instead of a stub: Twenty CRM, EspoCRM, ERPNext.
"""
import os
from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, make_asgi_app
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sdlc:sdlc_local_dev@postgres:5432/sdlc")
engine = create_engine(DATABASE_URL)

app = FastAPI(title="Integrated App Stack — Mock CRM", version="0.1.0")
app.mount("/metrics", make_asgi_app())

REQUEST_COUNT = Counter("crm_requests_total", "Total requests", ["endpoint"])


class Customer(BaseModel):
    name: str
    email: str


@app.on_event("startup")
def init_db():
    with engine.begin() as conn:
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
            """
        ))


@app.get("/health")
def health():
    return {"service": "ok"}


@app.get("/customers")
def list_customers():
    REQUEST_COUNT.labels(endpoint="/customers").inc()
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT id, name, email FROM customers")).mappings().all()
        return [dict(r) for r in rows]


@app.post("/customers")
def create_customer(customer: Customer):
    REQUEST_COUNT.labels(endpoint="/customers").inc()
    with engine.begin() as conn:
        result = conn.execute(
            text("INSERT INTO customers (name, email) VALUES (:name, :email) RETURNING id"),
            {"name": customer.name, "email": customer.email},
        )
        return {"id": result.scalar(), **customer.model_dump()}
