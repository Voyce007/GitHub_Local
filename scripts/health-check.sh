#!/usr/bin/env bash
# Checks every service that's currently running (per docker compose ps),
# not every service defined — services in profiles you haven't started
# are expected to be absent.
set -uo pipefail

check() {
  local name="$1" url="$2"
  if curl -sf -o /dev/null --max-time 3 "$url"; then
    echo "OK    $name  ($url)"
  else
    echo "DOWN  $name  ($url)"
  fi
}

echo "== Layer 1: Infrastructure =="
check "LocalStack" "http://localhost:4566/_localstack/health"
check "Keycloak"   "http://localhost:8080/realms/master"

echo "== Layer 2: Data / KX Backbone =="
check "Ollama"   "http://localhost:11434/api/tags"
check "Qdrant"   "http://localhost:6333/collections"
check "MinIO"    "http://localhost:9000/minio/health/live"

echo "== Layer 3: AI / Agent Backbone =="
check "agent-service" "http://localhost:8001/health"

echo "== Layer 4: Integrated App Stack =="
check "mock-crm-service" "http://localhost:8002/health"

echo "== Layer 5: Orchestration =="
check "mcp-server" "http://localhost:8003/mcp"
check "Traefik"    "http://localhost:8090"

echo "== Layer 6: Agentic Comms =="
check "Open WebUI" "http://localhost:3000"

echo "== Layer 7: Observability & FinOps =="
check "Prometheus" "http://localhost:9090/-/healthy"
check "Grafana"    "http://localhost:3001/api/health"
