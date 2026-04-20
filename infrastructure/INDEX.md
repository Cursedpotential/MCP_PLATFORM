# Infrastructure — Agent Index
> Read parent INDEX.md before this one.
> Check local TODO.md for approved tasks before starting work.

---


## I need to work on Docker / services
→ `docker-compose.yml` (root) — all service definitions
→ `TODO.md` — infrastructure tasks in order (INFRA-001 through INFRA-009)
→ IMPORTANT: No container may start without "approved — proceed" from Matt

## I need to work on Keycloak
→ Infrastructure AGENTS.md — Keycloak patterns
→ All services must register as Keycloak OIDC clients before exposure

## I need to work on Caddy routing
→ `infrastructure/Caddyfile`

## I need to work on PostgreSQL initialization
→ `infrastructure/init/postgres/` — init scripts 00-03

## I need to work on the audit logger
→ `infrastructure/interceptors/audit_logger/`

## I need to work on Directus
→ `infrastructure/directus/` — extensions + flows
→ REQUIRES CONTAINER GATE APPROVAL before starting

## I need to check last session state
→ `memory/MEMORY.md`

## Rules specific to infrastructure
→ `AGENTS.md`
