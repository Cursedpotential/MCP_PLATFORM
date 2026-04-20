# Py MCP Server TODO
> Read parent first: mcp-servers/TODO.md
> Only Matt can move tasks from READY → APPROVED.
> Agents update IN_PROGRESS and DONE as they work. Commit after every change.

---

## Status Key: IDEA → READY → APPROVED → IN_PROGRESS → DONE → DEFERRED → BLOCKED

## Active Tasks

| ID | Task | Status | Approved | Depends On | Assigned Session |
|----|------|--------|----------|------------|-----------------|
| PY-001 | EmbeddingService implementation (sentence-transformers, local) | BLOCKED | NO | OQ-5 — model selection pending | — |
| PY-002 | LanceDB batch upsert write path | READY | NO | PY-001 | — |
| PY-003 | Wire EmbeddingService to post-parse pipeline | READY | NO | PY-001 PY-002 | — |
| PY-004 | evidence_search MCP tool (semantic + keyword, LanceDB + pgvector) | READY | NO | PY-002 | — |
| PY-005 | Pattern analyzer port from Alpha 1 analysis/ | READY | NO | — | — |
| PY-006 | HurtLex integration port from Alpha 1 nlp/ | READY | NO | — | — |
| PY-007 | NER extraction → Neo4j entity nodes (Semantica) | READY | NO | — | — |
| PY-008 | Relation extraction → Neo4j edges | READY | NO | PY-007 | — |
| PY-009 | Document intelligence EngineRouter interface definition | READY | NO | — | — |
| PY-010 | Pandoc engine: stub → working local implementation | READY | NO | PY-009 | — |
| PY-011 | Tesseract OCR engine: stub → working local implementation | READY | NO | PY-009 | — |

---

## Completed Tasks

| ID | Task | Completed | Session |
|----|------|-----------|---------|
| — | (none yet) | — | — |
