# Layer 1 — Infrastructure

Local open source equivalents of AWS/Azure/GCP/Sovereign compute, networking, and IAM.

| Service | Image | Port | Purpose |
|---|---|---|---|
| LocalStack | `localstack/localstack` | 4566 | AWS API emulation (S3, IAM, Lambda, DynamoDB, STS, Secrets Manager) |
| Keycloak | `quay.io/keycloak/keycloak` | 8080 | Identity / IAM (OIDC) |

Start: `docker compose --profile infrastructure up -d`

See `.claude/skills/infrastructure-layer/SKILL.md` for implementation patterns.
