---
name: ci-cd
description: Use this skill whenever adding, modifying, or debugging CI/CD for a repo that platforms this tooling, or when adding/removing a service from its services.yaml. Trigger on "add CI for the new service", "why did the build fail", "cut a release", "add a staging deploy". Read this before editing any services.yaml or touching the wrapper workflows.
---

# CI/CD tooling — how this repo's pipeline actually works

This repo's pipeline is generic and config-driven: `.github/workflows/ci.yml`
and `release.yml` never name a service. They read a `services.yaml` file
(path passed via `services_config`) and build a matrix from it. All stack
knowledge lives in that one file — not in the workflows.

## Where the config lives

- **This repo, standalone use**: `config/services.yaml` (copy from
  `config/services.example.yaml`).
- **Platformed onto another repo**: a config file that lives in *that*
  repo (e.g. `ci-cd/services.yaml`), referenced by a thin wrapper
  workflow via `uses:` + `with: services_config:`. See
  `adapters/<name>/INTEGRATION.md` for a worked example.

## Adding a service

Never edit the workflow YAML to add a service — add an entry to
`services.yaml`:

```yaml
services:
  - name: my-new-service
    path: path/to/my-new-service   # must contain a Dockerfile
    port: 8010
    health_path: /health
    health_expect_non_200: true    # only if 200 isn't the right success signal
```

If the target repo has a `docker-compose.yml`, also add `smoke_profiles`
(or extend the existing list) so `smoke-test` brings the new service up
alongside its dependencies.

## The health_expect_non_200 escape hatch

Some services correctly respond with a non-200 to a plain `curl` (an MCP
streamable-http endpoint rejecting a non-streaming client is a real
example, not a bug) while still being genuinely up. Setting
`health_expect_non_200: true` makes the smoke-test treat *any* response
(vs. a connection failure) as success for that service, instead of
requiring exactly 200. Don't reach for this to paper over an actually
broken health check — only use it when you've confirmed the non-200 is
expected behavior.

## Standalone vs. platformed — what changes, what doesn't

| | Standalone | Platformed |
|---|---|---|
| Workflow files | This repo's `ci.yml`/`release.yml` run directly | Target repo has a thin wrapper calling this repo's workflows via `workflow_call` |
| `services.yaml` | `config/services.yaml` in this repo | Lives in the target repo, path passed as `services_config` |
| Pipeline logic (lint/build/scan/smoke/release) | Same in both cases — defined once, here | Same in both cases — defined once, here |

When a fix or new capability is needed (a new scanner, a signing change),
make it here, tag a new version, and every platformed repo picks it up
by bumping the `@vX` ref in its wrapper — don't fork the workflow logic
into the target repo to make a one-off change.

## Common tasks

| Task | Where to look |
|---|---|
| CI failing on a specific service's build | `services.yaml` for that entry's `path`/Dockerfile |
| A service's health check flaps in CI | Check if it needs `health_expect_non_200`, or fix the actual health endpoint — don't just raise retries |
| Cut a release for a platformed repo | Tag the *platformed* repo (its wrapper's `release.yml` trigger), not this tooling repo |
| Add staging/prod deploy | `release-bundle` job in `release.yml` is the ceiling by design; a k8s job is intentionally not included here — add it in the platformed repo's own workflow if/when it's needed, calling this repo's `ci.yml`/`release.yml` for the build/scan/sign portion only |
