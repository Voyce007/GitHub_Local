"""
Integrated App Stack (Layer 4)
────────────────────────────────
A minimal browser UI for mock-erp-service. Server-side proxies the /api/*
routes to ERP_SERVICE_URL so the frontend never needs to know the domain
service's network address (works the same from localhost or behind
Traefik) and CORS never becomes an issue.
"""
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from prometheus_client import Counter, make_asgi_app
import httpx

ERP_SERVICE_URL = os.getenv("ERP_SERVICE_URL", "http://mock-erp-service:8004")

app = FastAPI(title="Integrated App Stack — ERP UI", version="0.1.0")
app.mount("/metrics", make_asgi_app())

REQUEST_COUNT = Counter("erp_ui_requests_total", "Total requests", ["endpoint"])


@app.get("/health")
def health():
    return {"service": "ok"}


async def _proxy(method: str, path: str, json: dict | None = None):
    async with httpx.AsyncClient(base_url=ERP_SERVICE_URL, timeout=5.0) as client:
        try:
            resp = await client.request(method, path, json=json)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"mock-erp-service unreachable: {exc}")
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.json().get("detail", resp.text))
    return resp.json()


@app.get("/api/products")
async def api_list_products():
    REQUEST_COUNT.labels(endpoint="/api/products").inc()
    return await _proxy("GET", "/products")


@app.post("/api/products")
async def api_create_product(request: Request):
    REQUEST_COUNT.labels(endpoint="/api/products").inc()
    return await _proxy("POST", "/products", json=await request.json())


@app.get("/api/orders")
async def api_list_orders():
    REQUEST_COUNT.labels(endpoint="/api/orders").inc()
    return await _proxy("GET", "/orders")


@app.post("/api/orders")
async def api_create_order(request: Request):
    REQUEST_COUNT.labels(endpoint="/api/orders").inc()
    return await _proxy("POST", "/orders", json=await request.json())


@app.get("/", response_class=HTMLResponse)
def index():
    return INDEX_HTML


INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mock ERP</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }
  h1 { margin-bottom: 0.25rem; }
  .sub { color: #888; margin-top: 0; }
  section { margin-top: 2rem; }
  table { width: 100%; border-collapse: collapse; margin-top: 0.75rem; }
  th, td { text-align: left; padding: 0.4rem 0.6rem; border-bottom: 1px solid #8884; }
  form { display: flex; gap: 0.5rem; margin-top: 0.75rem; flex-wrap: wrap; align-items: center; }
  input, select { padding: 0.4rem; border-radius: 4px; border: 1px solid #8886; }
  button { padding: 0.4rem 0.9rem; border-radius: 4px; border: none; background: #4f46e5; color: white; cursor: pointer; }
  button:hover { background: #4338ca; }
  .error { color: #dc2626; margin-top: 0.5rem; }
  .low { color: #dc2626; font-weight: 600; }
</style>
</head>
<body>
  <h1>Mock ERP</h1>
  <p class="sub">Layer 4 — products &amp; orders, backed by mock-erp-service</p>

  <section>
    <h2>Products</h2>
    <table id="products-table">
      <thead><tr><th>SKU</th><th>Name</th><th>Stock</th></tr></thead>
      <tbody></tbody>
    </table>
    <form id="product-form">
      <input name="sku" placeholder="SKU" required>
      <input name="name" placeholder="Name" required>
      <input name="stock_qty" type="number" min="0" value="0" placeholder="Stock qty" required>
      <button type="submit">Add product</button>
    </form>
    <p class="error" id="product-error"></p>
  </section>

  <section>
    <h2>Orders</h2>
    <table id="orders-table">
      <thead><tr><th>ID</th><th>SKU</th><th>Qty</th><th>Status</th></tr></thead>
      <tbody></tbody>
    </table>
    <form id="order-form">
      <select name="sku" id="order-sku" required></select>
      <input name="quantity" type="number" min="1" value="1" placeholder="Quantity" required>
      <button type="submit">Place order</button>
    </form>
    <p class="error" id="order-error"></p>
  </section>

<script>
async function loadProducts() {
  const res = await fetch('/api/products');
  const products = await res.json();
  const tbody = document.querySelector('#products-table tbody');
  tbody.innerHTML = '';
  const sel = document.getElementById('order-sku');
  sel.innerHTML = '';
  for (const p of products) {
    const row = document.createElement('tr');
    row.innerHTML = `<td>${p.sku}</td><td>${p.name}</td><td class="${p.stock_qty < 5 ? 'low' : ''}">${p.stock_qty}</td>`;
    tbody.appendChild(row);
    const opt = document.createElement('option');
    opt.value = p.sku;
    opt.textContent = `${p.sku} (${p.stock_qty} in stock)`;
    sel.appendChild(opt);
  }
}

async function loadOrders() {
  const res = await fetch('/api/orders');
  const orders = await res.json();
  const tbody = document.querySelector('#orders-table tbody');
  tbody.innerHTML = '';
  for (const o of orders) {
    const row = document.createElement('tr');
    row.innerHTML = `<td>${o.id}</td><td>${o.sku}</td><td>${o.quantity}</td><td>${o.status}</td>`;
    tbody.appendChild(row);
  }
}

document.getElementById('product-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = document.getElementById('product-error');
  errEl.textContent = '';
  const form = new FormData(e.target);
  const body = { sku: form.get('sku'), name: form.get('name'), stock_qty: Number(form.get('stock_qty')) };
  const res = await fetch('/api/products', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
  if (!res.ok) { errEl.textContent = (await res.json()).detail || 'Failed to add product'; return; }
  e.target.reset();
  await loadProducts();
});

document.getElementById('order-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = document.getElementById('order-error');
  errEl.textContent = '';
  const form = new FormData(e.target);
  const body = { sku: form.get('sku'), quantity: Number(form.get('quantity')) };
  const res = await fetch('/api/orders', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
  if (!res.ok) { errEl.textContent = (await res.json()).detail || 'Failed to place order'; return; }
  e.target.reset();
  await Promise.all([loadProducts(), loadOrders()]);
});

loadProducts();
loadOrders();
</script>
</body>
</html>
"""
