---
name: infrastructure-layer
description: Use when provisioning compute, networking, IAM, or cloud-service emulation for this architecture — e.g. adding a new AWS/Azure/GCP-equivalent capability, setting up identity/auth, or changing how services reach the "cloud." Trigger on mentions of LocalStack, Keycloak, IAM, networking, or "infrastructure layer."
---

# Layer 1 — Infrastructure

Open source local equivalents of the deck's "AWS · Azure · GCP · Sovereign —
compute, networking, IAM":

| Deck concept | Local implementation |
|---|---|
| Compute | Docker Desktop or Colima (Colima recommended on Mac — lighter, no license) |
| Cloud APIs (S3, IAM, Lambda, DynamoDB, STS, Secrets Manager) | LocalStack |
| Identity / IAM | Keycloak |
| Networking | docker-compose bridge network `sdlc-net`; Traefik (layer 5) for ingress |
| Sovereign/data-residency requirement | Everything runs on-laptop by construction — no data leaves the machine unless you point a service at a real cloud endpoint |

## Working in this layer

1. **Adding an AWS-shaped capability**: enable it in the `localstack`
   service's `SERVICES` env var in `docker-compose.yml`, then point your
   application code at `http://localstack:4566` (from other containers) or
   `http://localhost:4566` (from the host) with dummy credentials
   (`test`/`test` — LocalStack doesn't validate them). Use the AWS SDK/CLI
   exactly as you would against real AWS; only the endpoint URL changes.
2. **Adding a realm/client for IAM**: use the Keycloak admin console at
   `localhost:8080` (admin/admin — change before this ever leaves your
   laptop) or its REST admin API. Create one realm per "tenant" if you're
   modeling multi-tenant access; issue OIDC clients per service that needs
   to authenticate.
3. **Promoting to real cloud later**: because application code talks to
   these via standard AWS SDKs / OIDC, moving a layer-1 capability to real
   AWS/Azure/GCP is an endpoint + credential swap, not a rewrite — keep it
   that way. Don't let application code special-case LocalStack.

## Testing

- `curl http://localhost:4566/_localstack/health` — confirms which AWS
  services are active.
- `curl http://localhost:8080/realms/master` — confirms Keycloak is up.
- Resource check before starting this layer: LocalStack + Keycloak add
  roughly 1.5–2GB RAM on top of core. Skip this profile entirely for tasks
  that don't need cloud-API emulation or IAM.

## Gotchas

- LocalStack persists state in the `localstack-data` volume — `docker
  compose down -v` wipes emulated S3 buckets etc. Use `down` (no `-v`) to
  keep them.
- Keycloak's `start-dev` command is for local development only; it's
  intentionally not hardened (no HTTPS, in-memory-friendly config).
