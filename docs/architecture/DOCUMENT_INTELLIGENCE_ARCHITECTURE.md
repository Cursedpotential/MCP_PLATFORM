# Document Intelligence Architecture — MCP Platform

> ⚠️ **PLANNING DOCUMENT — NOT AUTHORIZATION**: Nothing in this document is permission to implement. Each phase, major task, and architectural decision requires explicit owner approval before any code is written or any service is activated.

---

## Overview

The MCP Platform document intelligence system uses a **pluggable router architecture** to process documents through the best available engine for each document type, cost tolerance, and privacy constraint. Rather than committing to a single engine, the system defines a common `EngineRouter` interface that all 11 supported engines implement. Engines are opt-in — only engines with available runtimes or credentials activate.

This architecture was formally adopted in ADR-023 and ADR-024. See `DECISION_REGISTER.md`.

---

## Engine Comparison Matrix

| Engine | Best For | Locality | Cost | Formats | Key Strength |
|--------|----------|----------|------|---------|-------------|
| **Pandoc** | Format conversion (DOCX, HTML, RTF, EPUB → text/Markdown) | Local only | Free | DOCX, HTML, RTF, EPUB, ODT, LaTeX, many more | Broadest format support; zero data egress |
| **Tesseract** | Standard printed text OCR | Local only | Free | PNG, JPEG, TIFF, PDF (rasterized) | Battle-tested, 100+ languages, no network |
| **DocTR** | Modern neural document OCR | Local only | Free (GPU optional) | PNG, JPEG, PDF | Higher accuracy than Tesseract on complex layouts |
| **Docling** (IBM) | Rich document structure extraction (tables, figures, sections) | Local capable | Free (open source) | PDF, DOCX, HTML | Deep structural understanding beyond text extraction |
| **OCRopus** | Historical or degraded document OCR | Local only | Free | PNG, TIFF | Specialized for aged/handwritten documents |
| **Unstructured.io** | Multi-format extraction (email, slides, spreadsheets) | Local or API | Free (local) / Paid (API) | PDF, DOCX, PPTX, XLSX, EML, HTML, images | Broadest non-document format support |
| **GLM-OCR** | AI-vision OCR with multimodal context | Local (LLM) | Free (model weights) | Images, PDFs | Handles context-dependent text interpretation |
| **LlamaParse** | Complex PDF parsing (tables, figures, multi-column) | Cloud API | Per-page cost | PDF, DOCX | Best-in-class for complex PDF layouts |
| **Google DocAI** | Forms, structured documents, government ID | Cloud API | Per-page cost | PDF, images | Unmatched form field extraction and entity detection |
| **AWS Textract** | Table and form data extraction | Cloud API | Per-page cost | PDF, images | Strong table cell extraction, AWS integration |
| **IBM watsonx** | Enterprise document understanding | Cloud API | Enterprise pricing | PDF, DOCX, images | Deep integration with IBM enterprise stack |

---

## Package Structure

```
mcp-servers/py-mcp-server/src/
├── document_intelligence/
│   ├── __init__.py
│   ├── engine_router.py          # EngineRouter interface + routing logic
│   ├── engine_base.py            # BaseEngine abstract class
│   ├── routing_config.py         # Cost/privacy/fallback configuration
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── pandoc_engine.py      # [stub → working in Phase 1]
│   │   ├── tesseract_engine.py   # [stub → working in Phase 1]
│   │   ├── doctr_engine.py       # [stub only in Phase 1; working in Phase 2]
│   │   ├── docling_engine.py     # [stub only in Phase 1; working in Phase 2]
│   │   ├── ocropus_engine.py     # [stub only]
│   │   ├── unstructured_engine.py # [stub only]
│   │   ├── glm_ocr_engine.py     # [planned]
│   │   ├── llamaparse_engine.py  # [deferred — cloud]
│   │   ├── google_docai_engine.py # [deferred — cloud]
│   │   ├── aws_textract_engine.py # [deferred — cloud]
│   │   └── watsonx_engine.py     # [deferred — cloud]
│   └── tests/
│       ├── test_engine_router.py
│       ├── test_pandoc_engine.py
│       └── test_tesseract_engine.py
```

---

## Routing Logic

### Document Type Detection

Before routing, the system detects the document type:

```
Input document
      │
      ▼
1. Check MIME type (Content-Type header or file magic bytes)
2. Check file extension
3. If ambiguous: sample content inspection
      │
      ▼
Document type classification:
  - text/plain, text/markdown → skip engine, return as-is
  - application/vnd.openxmlformats-officedocument.* → Pandoc
  - text/html → Pandoc
  - application/pdf (text-bearing) → Pandoc → Docling fallback
  - application/pdf (scanned) → Tesseract → DocTR fallback
  - image/* → Tesseract → DocTR fallback
  - application/vnd.ms-excel, .xlsx → Unstructured
  - message/rfc822 (email) → Unstructured
  - application/vnd.ms-powerpoint → Unstructured
  - historical/degraded image → OCRopus
  - unknown → attempt Pandoc, then Tesseract, then error
```

### Fallback Chain

The router attempts engines in order until one succeeds or the chain is exhausted:

```python
FALLBACK_CHAINS = {
    "pdf_text":      ["pandoc", "docling", "llamaparse*", "google_docai*"],
    "pdf_scanned":   ["tesseract", "doctr", "google_docai*", "aws_textract*"],
    "image":         ["tesseract", "doctr", "glm_ocr", "google_docai*"],
    "docx":          ["pandoc", "docling", "unstructured"],
    "html":          ["pandoc", "unstructured"],
    "spreadsheet":   ["unstructured", "aws_textract*"],
    "email":         ["unstructured"],
    "historical":    ["ocropus", "tesseract", "doctr"],
    "unknown":       ["pandoc", "tesseract", "unstructured"],
}
# Engines marked * are cloud — only used if:
#   1. All local engines in the chain have failed
#   2. The engine is configured (credentials present)
#   3. Cloud routing is explicitly enabled in config
```

### Opt-In Activation

Each engine has an `is_available()` method that the router checks before attempting:

```python
class BaseEngine:
    def is_available(self) -> bool:
        """Return True only if this engine's runtime/credentials are present and valid."""
        raise NotImplementedError

    def process(self, document: DocumentInput) -> ExtractionResult:
        raise NotImplementedError
```

An engine that returns `False` from `is_available()` is silently skipped and the fallback chain continues. This means:
- Local engines are available as soon as their binary/model is in the Docker image
- Cloud engines are available only when credentials are configured AND cloud routing is enabled

---

## Fallback Chain Examples

### Example 1: Complex PDF with embedded text
```
Input: financial_report.pdf (text-bearing, no scan)
Chain: pandoc → docling → llamaparse*

Step 1: pandoc.is_available() → True
Step 2: pandoc.process(doc) → success
Result: Pandoc extraction returned. Chain stops.
```

### Example 2: Scanned government document (local only)
```
Input: id_scan.jpg (degraded scan, no cloud allowed)
Chain: tesseract → doctr → google_docai* [BLOCKED]

Step 1: tesseract.is_available() → True
Step 2: tesseract.process(doc) → low confidence result (0.42)
Step 3: Confidence below threshold (0.70) → continue chain
Step 4: doctr.is_available() → True
Step 5: doctr.process(doc) → confidence 0.89
Result: DocTR extraction returned. Chain stops.
Note: google_docai skipped — cloud routing disabled.
```

### Example 3: DOCX file
```
Input: contract.docx
Chain: pandoc → docling → unstructured

Step 1: pandoc.is_available() → True
Step 2: pandoc.process(doc) → success
Result: Pandoc extraction returned. Full structural Markdown.
```

### Example 4: Email archive (MBOX)
```
Input: inbox.mbox
Chain: unstructured

Step 1: unstructured.is_available() → True
Step 2: unstructured.process(doc) → success
Result: Unstructured extraction returned (per-message objects).
```

---

## Integration with the Ingestion Pipeline

The document intelligence router integrates with the ingestion pipeline as a conditional step:

```
ingest_evidence (MCP Tool) receives: { file_path, format_hint? }
        │
        ▼
[Format detection] — is this a messaging format or a document?
        │
        ├── Messaging format (SMS XML, Facebook JSON, iMessage) → messaging parser
        └── Document format → EngineRouter
                │
                ▼
        [EngineRouter.route(document)]
                │
                ▼
        ExtractionResult {
          text: string,
          structure: DocumentStructure?,
          confidence: float,
          engine_used: string,
          page_count: int?,
          warnings: string[]
        }
                │
                ▼
        [Normalize to EvidenceBatch]
                │
                ▼
        [SHA-256 fingerprint] → DuckDB
                │
                ▼
        [PostgreSQL write] → evidence_documents table
                │
                ▼
        [Embed text] → LanceDB + pgvector
```

---

## Cost and Privacy Decision Tree

```
Document received
      │
      ▼
Is document content sensitive (forensic evidence)?
      │
      ├── YES → Prefer local engines. Use cloud only if:
      │          (a) Local engines all failed
      │          (b) Owner has explicitly approved cloud for this document class
      │          (c) Cloud engine config is present
      │
      └── NO → Standard routing applies (local first, cloud as fallback)
                      │
                      ▼
              Is a local engine available for this document type?
                      │
                      ├── YES → Use local engine
                      └── NO  → Is cloud routing enabled?
                                      │
                                      ├── YES (approved) → Use cloud engine
                                      └── NO → Return error: "no engine available"
```

**Default configuration**: Cloud routing is **disabled** at startup. It must be explicitly enabled via environment variable after owner approval.

```bash
# Default: cloud routing disabled
DOCUMENT_INTELLIGENCE_CLOUD_ENABLED=false

# To enable (requires owner approval first):
DOCUMENT_INTELLIGENCE_CLOUD_ENABLED=true
GOOGLE_DOCAI_PROJECT_ID=...
GOOGLE_DOCAI_LOCATION=...
# etc.
```

---

## Implementation Status by Engine

| Engine | Status | Docker Image Change | Credential Required | Phase |
|--------|--------|--------------------|--------------------|-------|
| Pandoc | 🔜 Stub → working | Add `pandoc` binary | None | Phase 1 |
| Tesseract | 🔜 Stub → working | Add `tesseract-ocr` | None | Phase 1 |
| DocTR | ⚠️ Stub only | Add model weights | None | Phase 2 |
| Docling | ⚠️ Stub only | Add `docling` package | None | Phase 2 |
| OCRopus | ⚠️ Stub only | Add `ocropus` package | None | Phase 2 |
| Unstructured | ⚠️ Stub only | Add `unstructured` package | None (local mode) | Phase 2 |
| GLM-OCR | 🔜 Planned | Add model weights | None | Phase 2 |
| LlamaParse | ❌ Deferred | None | LlamaCloud API key | Phase 2+ (cloud approval) |
| Google DocAI | ❌ Deferred | None | GCP service account | Phase 2+ (cloud approval) |
| AWS Textract | ❌ Deferred | None | AWS credentials | Phase 2+ (cloud approval) |
| IBM watsonx | ❌ Deferred | None | IBM Cloud API key | Phase 2+ (cloud approval) |

---

## Integration with py-mcp-server MCP Tools

The document intelligence system registers 6 MCP tools in `py-mcp-server`:

| Tool Name | Description | Input | Output |
|-----------|-------------|-------|--------|
| `detect_document_type` | Detect MIME type and document class | `{ file_path: string }` | `{ mime_type, document_class, confidence }` |
| `extract_document_text` | Extract text from document using best available engine | `{ file_path, document_class?, force_engine? }` | `ExtractionResult` |
| `list_available_engines` | List currently available engines and their capabilities | `{}` | `{ engines: EngineInfo[] }` |
| `get_engine_status` | Get health and availability of a specific engine | `{ engine_name: string }` | `{ available, version, capabilities }` |
| `route_document` | Full routing: detect type + extract text + return with metadata | `{ file_path, allow_cloud?: boolean }` | `ExtractionResult + routing_trace` |
| `benchmark_engines` | Run a document through all available engines and compare results | `{ file_path }` | `{ results: EngineResult[], comparison }` |

All tools are registered in `py-mcp-server`'s tool manifest and dispatched through DIAL Core.

---

## Future Work

The following capabilities are not in scope for the current phases but should be considered in future design:

- **Streaming extraction**: For very large documents, stream extraction results rather than buffering the full output
- **Multi-page confidence aggregation**: Aggregate per-page confidence scores into a document-level confidence
- **Layout-aware chunking**: Split extracted text into semantically coherent chunks (paragraphs, sections) for better embedding
- **Table extraction**: Preserve table structure in a queryable format (not just flattened text)
- **Figure/image extraction**: Extract embedded figures and route them through the image OCR pipeline
- **Document classification**: Classify document type (contract, government ID, correspondence, financial) before routing
- **Multi-engine ensemble**: Run multiple engines on high-value documents and merge results for higher confidence
- **Cache layer**: Cache extraction results by SHA-256 to avoid re-processing identical documents

---

*Last updated: see git log*
