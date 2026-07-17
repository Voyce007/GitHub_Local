# Layer 6 — Agentic Comms Layer

Open WebUI provides the default human-facing chat interface over Ollama.

Start: `docker compose --profile comms up -d`, then open `http://localhost:3000`.

Bespoke copilot UIs (embedded in a specific workflow) get their own
sub-folder here — see `.claude/skills/agentic-comms/SKILL.md` for the
pattern and for wiring Open WebUI to `agent-service` instead of raw Ollama.
