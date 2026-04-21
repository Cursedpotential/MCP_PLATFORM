# AGENTS.md — infrastructure/

> Domain rules for infrastructure. Read after root AGENTS.md.

## This domain owns
Docker Compose, Conductor OSS (when deployed), ContextForge config, Keycloak, Caddy, Redis, Elasticsearch/Postgres backend for Conductor, init SQL, environment configs.

## CONDUCTOR GATE (hard stop)
Conductor infrastructure work does NOT begin until first end-to-end ingest test passes.
Gate condition: one evidence file fully ingested → hashed → stored → retrievable.

## Container start gate
No container starts without: `approved — proceed [service: name]`
This applies to EVERY container. No exceptions. Not even "just to test."

## Domain-specific rules
- All secrets go in `.env`. Nothing hardcoded in any config file.
- Schema changes require a numbered migration file: `migrations/00N_description.sql`
- Caddy config change = REQUIRES_CONFIRMATION (it's the external boundary)
- Keycloak client additions = REQUIRES_CONFIRMATION (auth surface change)
- Do not reference DIAL Core, DIAL Chat, or dial-stack in any new infrastructure config.

## Conductor skill
For all Conductor server setup, worker deployment, and workflow definition work, load:
`docs/wiki/skills/orchestration/conductor/SKILL.md`

For CONDUCTOR GATE status and open questions (OQ-C1 through OQ-C5):
`docs/wiki/skills/orchestration/conductor/OVERVIEW.md`
`docs/wiki/skills/orchestration/conductor/PLATFORM_IMPLEMENTATION.md`

## Read next
`infrastructure/memory/MEMORY.md` → `infrastructure/TODO.md` → `infrastructure/INDEX.md`

*Last updated: 2026-04-21*
