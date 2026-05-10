# Infrastructure TODO
> Read parent first: TODO.md (root)
> Only Matt can move tasks from READY → APPROVED.
> Agents update IN_PROGRESS and DONE as they work. Commit after every change.

---

## Status Key: IDEA → READY → APPROVED → IN_PROGRESS → DONE → DEFERRED → BLOCKED

## Active Tasks

| ID | Task | Status | Approved | Depends On | Assigned Session |
|----|------|--------|----------|------------|-----------------|
| INFRA-001 | Verify all docker-compose service definitions are correct | READY | NO | — | — |
| INFRA-002 | Start PostgreSQL container — verify migrations 001-005 applied | READY | NO | INFRA-001 | — |
| INFRA-003 | Start Neo4j container — verify evidence_graph DB accessible | READY | NO | INFRA-001 | — |
| INFRA-004 | Verify Keycloak container and OIDC config | READY | NO | INFRA-001 | — |
| INFRA-005 | Directus container activation — configure PostgreSQL connection | READY | NO | INFRA-002 — REQUIRES CONTAINER GATE APPROVAL | — |
| INFRA-006 | Directus RBAC setup (admin vs reviewer roles) | READY | NO | INFRA-005 | — |
| INFRA-007 | Caddy routing verification | READY | NO | INFRA-001 | — |
| INFRA-008 | OpenWebUI container definition (commented out until approved) | READY | NO | INFRA-005 — REQUIRES INDIVIDUAL APPROVAL | — |
| INFRA-009 | LibreChat container definition (commented out until approved) | READY | NO | INFRA-005 — REQUIRES INDIVIDUAL APPROVAL | — |

---

## Completed Tasks

| ID | Task | Completed | Session |
|----|------|-----------|---------|
| — | (none yet) | — | — |
