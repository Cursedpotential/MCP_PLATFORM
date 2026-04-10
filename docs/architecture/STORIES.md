---
title: Reverse-Engineered Stories
reviewed: 2026-04-08
revision: 1
author: Codex
status: current
---

# Epics and Stories

This document infers likely product and developer intent from the checked-in code and configuration. It describes what the repository appears to support today, not what earlier planning documents hoped to ship.

Sources: `docker-compose.yml`, `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/py-mcp-server/src/server.py`, `infrastructure/core/config.json`, `client/src/App.tsx`

## Epics

### Evidence Ingestion

Goal: turn exported message files into normalized records with chain-of-custody metadata.

### Semantic Analysis

Goal: run NLP, graph, vector, and identification workflows on extracted text.

### Human Review and Administration

Goal: let operators manage prompts/providers and review low-confidence outputs.

### Stack Operations

Goal: run the platform as a containerized DIAL-based system with authentication and routing.

Sources: `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/py-mcp-server/src/server.py`, `docker-compose.yml`, `infrastructure/settings/settings.json`

## User Stories

### Evidence Ingestion

- As an analyst, I want to parse SMS XML, Facebook export, and iMessage PDF files so that message data becomes structured output.
  Main entry points: `parse_sms_xml`, `parse_facebook_export`, `parse_imessage_pdf` in `mcp-servers/ts-mcp-server/src/index.ts`; parser classes in `mcp-servers/ts-mcp-server/src/tools/`
- As a forensic operator, I want ingestions logged with hashes and tier-write tracking so that chain of custody is preserved.
  Main entry points: `vault_log_ingestion`, `vault_get_pending_pass1`, `vault_update_pass1_status`, `vault_update_write_tracking` in `mcp-servers/ts-mcp-server/src/index.ts`

### Semantic Analysis

- As an analyst, I want entities, relations, temporal facts, and conflicts extracted from text so I can build semantic case context.
  Main entry points: `semantica_extract_entities`, `semantica_build_graph`, `semantica_extract_temporal_facts`, `semantica_detect_conflicts` in `mcp-servers/py-mcp-server/src/server.py`
- As an analyst, I want embedding generation and vector search so I can search evidence semantically.
  Main entry points: `semantica_generate_embeddings`, `lancedb_vector_search`, `lancedb_upsert`, `lancedb_list_collections`
- As a reviewer, I want quick identification passes for HAP, PII, language, readability, and document quality.
  Main entry points: `dpk_hap_score`, `dpk_pii_redact`, `dpk_lang_id`, `dpk_doc_quality`, `dpk_readability`
- As an investigator, I want workflow presets so I can run repeatable analysis bundles on text.
  Main entry points: `workflow_list`, `workflow_run`, `workflow_update_config`, `workflow_add_module`, `workflow_remove_module`; config in `mcp-servers/py-mcp-server/config/workflows.json`

### Human Review and Administration

- As an operator, I want to manage model providers and system prompts through MCP tools.
  Main entry points: `admin_list_llm_providers`, `admin_upsert_llm_provider`, `admin_list_system_prompts`, `admin_upsert_system_prompt`
- As a human reviewer, I want to inspect, approve, reject, and submit review items.
  Main entry points: `review_list_pending`, `review_approve`, `review_reject`, `review_submit`

### Stack Operations

- As a platform operator, I want containerized services for DIAL core, chat, auth, storage, and MCP servers so the system can run locally as one stack.
  Main entry points: `docker-compose.yml`, `infrastructure/core/config.json`, `infrastructure/settings/settings.json`
- As a developer, I want a separate planning workspace kept inside the documentation tree so historical plans stay discoverable without becoming the live system of record.
  Main entry points: `docs/wiki/plannotator/`, `.plannotator`, `docs/references/PLANNOTATOR.md`

Sources: `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/py-mcp-server/config/workflows.json`, `docker-compose.yml`, `docs/references/PLANNOTATOR.md`

## Change Log

- 2026-04-08, rev 1, Codex: created a reverse-engineered stories document based on the current repo rather than prior planning claims.
