# SBV Integration Spec

> **Status**: Implemented (Phase A)
> **Author**: Copilot
> **Date**: 2026-04-12

## Overview

SBV (SMS Backup Viewer, `ghcr.io/lowcarbdev/sbv:stable`) is integrated as a
Docker sidecar service.  It provides:

1. **Web UI** for browsing imported SMS/MMS/call XML backups
2. **REST API** that the platform's `SbvClient` calls to pull parsed data

All data pulled from SBV flows through the **existing chain-of-custody
evidence pipeline** — identical to `SmsEvidenceIngestor`.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  User drops XML file into SBV volume (/data/sbv)           │
│  or uploads via SBV web UI (http://localhost:8084)          │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
              ┌────────────────────────┐
              │   SBV Container        │
              │   (Go + SQLite)        │
              │   :8081 internal       │
              │   :8084 host-mapped    │
              └──────────┬─────────────┘
                         │  REST API (/api/*)
                         ▼
              ┌────────────────────────┐
              │  SbvClient.ts          │
              │  (session-cookie auth) │
              └──────────┬─────────────┘
                         │
                         ▼
              ┌────────────────────────┐
              │  SbvIngestor.ts        │
              │  Evidence Pipeline:    │
              │  1. SHA-256 hash       │
              │  2. DuckDB dedup       │
              │  3. UUIDv7             │
              │  4. Normalize → NM[]   │
              │  5. PG documents       │
              │  6. PG conversations   │
              │  7. PG messages        │
              │  8. Write tracking     │
              └────────────────────────┘
```

## Web UI Access

SBV's web interface is accessible two ways:

| Method | URL | Notes |
|--------|-----|-------|
| Direct | `http://localhost:8084` | Host-mapped port from docker-compose |
| Via Caddy proxy | `http://localhost/sbv/` | Caddy strips `/sbv` prefix, reverse-proxies to `sbv:8081` |

The Caddy route means the SBV UI is reachable from the same origin as DIAL
Chat and the Core API, allowing future integration into the navigation menu.

## MCP Tools

| Tool | Type | Pipeline | Description |
|------|------|----------|-------------|
| `sbv_ingest` | write | Full evidence pipeline | Pulls all conversations, messages, calls from SBV → hash → DuckDB → PG |
| `sbv_search` | read-only | None (direct SBV query) | Full-text search on SBV's SQLite — for quick lookups |
| `sbv_health` | read-only | None | Checks if SBV sidecar is reachable |

## Evidence Pipeline Compliance

The `SbvIngestor` follows the exact same chain-of-custody as `SmsEvidenceIngestor`:

1. **SHA-256 at first touch** — hash the raw API response JSON before any transformation
2. **DuckDB dedup** — `vault.getIngestionByHash(sourceHash)` — skip if duplicate
3. **DuckDB register** — `vault.logIngestion()` with UUIDv7, source_type `sbv_api_pull`
4. **Normalize** — `SbvMessage[]` → `NormalizedMessage[]` (reuses same interface)
5. **PostgreSQL writes** — `evidence.documents`, `evidence.conversations`, `evidence.messages`
6. **Content hash per message** — SHA-256 of `{raw_data, timestamp, sender, recipient, record_type}`
7. **Write tracking** — `vault.updateWriteTracking(ingestionId, 'postgresql', true)`

All messages written to PostgreSQL carry:
- `content_hash` (SHA-256, required by `PostgresWriter` chain-of-custody validation)
- `provenance` JSON with full hash-level audit trail
- `source: 'sbv'` marker for origin tracking

## Field Mapping

### Messages: SBV → NormalizedMessage

| SBV Field | NormalizedMessage Field | Notes |
|-----------|------------------------|-------|
| `body` | `text` | Trimmed; empty → skipped |
| `date` | `metadata.timestamp` | Parsed as epoch-ms or ISO |
| `address` | `metadata.raw_address` | Raw phone number |
| `contact_name` | `metadata.contact_name` | |
| `type` | `metadata.type_code` | 1=received, 2=sent |
| `read` | `metadata.read_status` | |
| `status` | `metadata.status_code` | |
| `msg_box` | `metadata.message_box` | |
| `parts[]` | `metadata.has_attachments`, `attachment_count` | Non-text parts counted |

### Calls: SBV → NormalizedMessage

| SBV Field | NormalizedMessage Field | Notes |
|-----------|------------------------|-------|
| `number` | `metadata.raw_address` | |
| `contact_name` | `metadata.contact_name` | |
| `date` | `metadata.timestamp` | |
| `duration` | `metadata.duration_seconds` | |
| `type` | `metadata.type_code` + `result_label` | Same call-type map as SmsXmlParser |

Forensic blocking flags (type 5, 6, outgoing+0-duration) are applied identically
to the SmsXmlParser logic.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SBV_URL` | `http://sbv:8081` | Internal Docker network URL for SBV |
| `SBV_USERNAME` | (empty) | SBV login username (empty = no-auth mode) |
| `SBV_PASSWORD` | (empty) | SBV login password |

## Docker Compose

```yaml
sbv:
  image: ghcr.io/lowcarbdev/sbv:stable
  restart: unless-stopped
  ports:
    - "8084:8081"
  environment:
    - PUID=1000
    - PGID=1000
  volumes:
    - sbv_data:/data
```

## Future Work

- [ ] Compare SBV's XML parsing logic with our `SmsXmlParser` for correctness improvements
- [ ] Add SBV link to the DIAL Chat sidebar or React client navigation menu
- [ ] Support incremental/delta ingestion (only new messages since last pull)
- [ ] Wire SBV import into the `EvidenceIngestor` format-dispatch for `.xml` files
