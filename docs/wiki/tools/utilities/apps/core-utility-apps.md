# Core Utility Apps

This page covers the top-level utility apps most likely to be adapted, wrapped, or reused directly.

## Chunker

- **Path**: `tools/utilities/Chunker`
- **What it is**: Python-based smart chunking application with UI and schema-aware chunking.
- **Why it matters**: Useful for splitting large documents, conversation logs, and evidence bundles into AI-friendly chunks.
- **How it might be implemented here**: as a preprocessing sidecar, as a script-backed utility for ingestion jobs, or as a future MCP wrapper for chunking operations.
- **Local sources**: `README.md`, `main.py`, `requirements.txt`

## ConversationExtractor

- **Path**: `tools/utilities/ConversationExtractor`
- **What it is**: Autopsy-oriented conversation extraction plugin that reconstructs SMS conversations from Android evidence.
- **Why it matters**: It maps directly to forensic conversation recovery and timeline reconstruction.
- **How it might be implemented here**: as a reference parser for SMS evidence extraction, or as a conversion/normalization step before storage in the evidence pipeline.
- **Local sources**: `README.md`, `ConversationExtractorModule.py`, `AndroidMsgParser.py`

## context-artifact-resolver

- **Path**: `tools/utilities/context-artifact-resolver`
- **What it is**: Node/Vite application generated from AI Studio-style scaffolding.
- **Why it matters**: likely useful for resolving context fragments, artifacts, or intermediate knowledge objects in a UI-first workflow.
- **How it might be implemented here**: as a review utility or adapted into a lightweight artifact-browser frontend.
- **Local sources**: `README.md`, `package.json`, `metadata.json`

## context-relay

- **Path**: `tools/utilities/context-relay`
- **What it is**: Node/Vite utility app with Gemini-oriented local-run instructions.
- **Why it matters**: suggests a relay pattern for moving or transforming context between systems or prompts.
- **How it might be implemented here**: as an orchestration or handoff utility between intake, prompting, and review workflows.
- **Local sources**: `README.md`, `package.json`, `metadata.json`

## inspector

- **Path**: `tools/utilities/inspector`
- **What it is**: vendored MCP Inspector source tree for testing and debugging MCP servers.
- **Why it matters**: directly useful for local MCP development, validation, and debugging.
- **How it might be implemented here**: as a local developer dependency and troubleshooting reference rather than a product feature.
- **Local sources**: `README.md`, `package.json`, `cli/`, `server/`, `client/`

## lexicon-analysis-engine

- **Path**: `tools/utilities/lexicon-analysis-engine`
- **What it is**: Node/Vite utility app likely intended for lexicon-driven analysis workflows.
- **Why it matters**: could support threat lexicons, abuse lexicons, or domain dictionaries in evidence review.
- **How it might be implemented here**: as an analysis helper tied to abusive-language, trigger, or semantic classification pipelines.
- **Local sources**: `README.md`, `package.json`, `metadata.json`

## rag-implementation

- **Path**: `tools/utilities/rag-implementation`
- **What it is**: staged RAG-oriented utility with a local `SKILL.md`.
- **Why it matters**: retrieval-augmented patterns are relevant to evidence summarization, context recall, and case-memory workflows.
- **How it might be implemented here**: as a reference pattern for local retrieval or as a skill-layer source.
- **Local sources**: `SKILL.md`

## stirling_pdf_tool

- **Path**: `tools/utilities/stirling_pdf_tool`
- **What it is**: staged PDF-processing utility aligned with Stirling PDF workflows.
- **Why it matters**: PDF normalization and extraction are common intake tasks.
- **How it might be implemented here**: as a document-processing sidecar or as a wrapper around PDF transformation tasks.
- **Local sources**: directory contents under `stirling_pdf_tool`

## xml-stream-processor

- **Path**: `tools/utilities/xml-stream-processor`
- **What it is**: staged XML processing utility.
- **Why it matters**: XML is a recurring evidence format, especially for message backups and exports.
- **How it might be implemented here**: as a streaming parser for large XML archives or SMS export inputs.
- **Local sources**: directory contents under `xml-stream-processor`

## xml-to-csv-converter

- **Path**: `tools/utilities/xml-to-csv-converter`
- **What it is**: Node/Vite utility app for XML-to-CSV workflows.
- **Why it matters**: quick tabular conversion can help analysts validate or export evidence data.
- **How it might be implemented here**: as a conversion helper for analyst review or as a staging tool before deeper parsing.
- **Local sources**: `README.md`, `package.json`, `metadata.json`

Sources: `tools/utilities/Chunker/README.md`, `tools/utilities/ConversationExtractor/README.md`, `tools/utilities/context-artifact-resolver`, `tools/utilities/context-relay/README.md`, `tools/utilities/inspector/README.md`, `tools/utilities/lexicon-analysis-engine`, `tools/utilities/rag-implementation/SKILL.md`, `tools/utilities/stirling_pdf_tool`, `tools/utilities/xml-stream-processor`, `tools/utilities/xml-to-csv-converter/README.md`
