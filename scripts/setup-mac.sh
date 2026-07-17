#!/usr/bin/env bash
# One-time setup for MacBook Pro (Ventura) — installs a container runtime
# and the Claude Code CLI, then pulls a default local model.
set -euo pipefail

echo "== Checking Homebrew =="
if ! command -v brew &>/dev/null; then
  echo "Homebrew not found. Install it from https://brew.sh first, then re-run this script."
  exit 1
fi

echo "== Installing Colima + Docker CLI (lighter than Docker Desktop) =="
brew install colima docker docker-compose

echo "== Starting Colima with sensible resource limits for a laptop =="
# Adjust --cpu/--memory to your machine. 4 CPU / 8GB is a safe default
# alongside the 'core' compose profile; bump memory if running 'full'.
colima start --cpu 4 --memory 8 --disk 60

echo "== Installing Claude Code CLI (if not already present) =="
if ! command -v claude &>/dev/null; then
  echo "Claude Code not found — install it per https://docs.claude.com/en/docs/claude-code"
  echo "(npm install -g @anthropic-ai/claude-code, or see the docs for the current method)"
fi

echo "== Bringing up the core profile =="
cd "$(dirname "$0")/.."
docker compose --profile core up -d

echo "== Pulling a default local model (this downloads several GB) =="
docker exec -it ollama-svc ollama pull llama3.1:8b || true

echo "== Done =="
echo "Chat UI:      http://localhost:3000"
echo "Agent service: http://localhost:8001/health"
echo "Next: run 'docker compose --profile orchestration up -d' then"
echo "  claude mcp add sdlc-stack --transport http http://localhost:8003/mcp"
