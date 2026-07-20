"""
Integrated App Stack (Layer 4)
────────────────────────────────
Stands in for a real ERP capability (inventory + orders). Shaped like a real
domain integration — a REST API in front of its own Postgres tables — so
Claude Code can later swap this for a real ERP connector (e.g. an SAP or
NetSuite adapter) without changing how layers 3/5/6 talk to it. Open source
real-ERP option if you want the genuine article instead of a stub: ERPNext.
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, make_asgi_app
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sdlc:sdlc_local_dev@postgres:5432/sdlc")
engine = create_engine(DATABASE_URL)

app = FastAPI(title="Integrated App Stack — Mock ERP", version="0.1.0")
app.mount("/metrics", make_asgi_app())

REQUEST_COUNT = Counter("erp_requests_total", "Total requests", ["endpoint"])


class Product(BaseModel):
    sku: str
    name: str
    stock_qty: int = 0


class Order(BaseModel):
    sku: str
    quantity: int


@app.on_event("startup")
def init_db():
    with engine.begin() as conn:
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS erp_products (
                id SERIAL PRIMARY KEY,
                sku TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                stock_qty INTEGER NOT NULL DEFAULT 0
            )
            """
        ))
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS erp_orders (
                id SERIAL PRIMARY KEY,
                sku TEXT NOT NULL REFERENCES erp_products(sku),
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'confirmed'
            )
            """
        ))


@app.get("/health")
def health():
    return {"service": "ok"}


@app.get("/products")
def list_products():
    REQUEST_COUNT.labels(endpoint="/products").inc()
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT id, sku, name, stock_qty FROM erp_products")).mappings().all()
        return [dict(r) for r in rows]


@app.post("/products")
def create_product(product: Product):
    REQUEST_COUNT.labels(endpoint="/products").inc()
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "INSERT INTO erp_products (sku, name, stock_qty) "
                "VALUES (:sku, :name, :stock_qty) RETURNING id"
            ),
            product.model_dump(),
        )
        return {"id": result.scalar(), **product.model_dump()}


@app.get("/orders")
def list_orders():
    REQUEST_COUNT.labels(endpoint="/orders").inc()
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT id, sku, quantity, status FROM erp_orders")).mappings().all()
        return [dict(r) for r in rows]


@app.post("/orders")
def create_order(order: Order):
    REQUEST_COUNT.labels(endpoint="/orders").inc()
    with engine.begin() as conn:
        stock = conn.execute(
            text("SELECT stock_qty FROM erp_products WHERE sku = :sku"),
            {"sku": order.sku},
        ).scalar()
        if stock is None:
            raise HTTPException(status_code=404, detail=f"unknown sku {order.sku!r}")
        if stock < order.quantity:
            raise HTTPException(status_code=409, detail="insufficient stock")

        conn.execute(
            text("UPDATE erp_products SET stock_qty = stock_qty - :qty WHERE sku = :sku"),
            {"qty": order.quantity, "sku": order.sku},
        )
        result = conn.execute(
            text("INSERT INTO erp_orders (sku, quantity) VALUES (:sku, :quantity) RETURNING id"),
            order.model_dump(),
        )
        return {"id": result.scalar(), "status": "confirmed", **order.model_dump()}
