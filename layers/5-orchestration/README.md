# Layer 5 — Orchestration

`mcp-server/` — a real Model Context Protocol server exposing the stack's
services as tools Claude Code can call. Traefik provides an API gateway.
Kubernetes (`kind`/`k3d`) is optional and not run by default — see the skill.

Start: `docker compose --profile orchestration up -d`

Register with Claude Code:
```bash
claude mcp add sdlc-stack --transport http http://localhost:8003/mcp
```

See `.claude/skills/orchestration/SKILL.md` for implementation patterns.
