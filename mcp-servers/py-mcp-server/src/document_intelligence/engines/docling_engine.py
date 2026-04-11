"""
IBM Docling engine adapter.

Strengths: Table extraction, document structure understanding,
multi-format (PDF/DOCX/PPTX/XLSX/HTML/images), markdown export for LLM consumption.
Best for: Complex PDFs with tables, structured documents, LLM-ready output.

Reference implementation: docs/wiki/tools/semantica/semantica/parse/docling_parser.py
"""

from __future__ import annotations

import logging
from typing import Any

from ..base import DocumentEngine
from ..models import DocumentIntelligenceResult, EngineCapability, CostTier, Locality

logger = logging.getLogger(__name__)


class DoclingEngine(DocumentEngine):
    @property
    def name(self) -> str:
        return "docling"

    @property
    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability.OCR,
            EngineCapability.TABLE_EXTRACTION,
            EngineCapability.LAYOUT_ANALYSIS,
            EngineCapability.CHUNKING,
            EngineCapability.RAG_NATIVE,
        ]

    @property
    def supported_formats(self) -> list[str]:
        return [".pdf", ".docx", ".pptx", ".xlsx", ".html", ".png", ".jpg", ".jpeg", ".tiff"]

    @property
    def cost_tier(self) -> CostTier:
        return CostTier.FREE

    @property
    def locality(self) -> Locality:
        return Locality.LOCAL

    def is_available(self) -> bool:
        try:
            import docling  # noqa: F401
            return True
        except ImportError:
            return False

    def process(self, file_path: str, task: str, options: dict[str, Any] | None = None) -> DocumentIntelligenceResult:
        """
        Process document using IBM Docling.

        Reference: docs/wiki/tools/semantica/semantica/parse/docling_parser.py
        TODO: Port full implementation from docling_parser.py reference when owner approves.
        """
        try:
            from docling.document_converter import DocumentConverter

            converter = DocumentConverter()
            result = converter.convert(file_path)
            doc = result.document

            # Extract text (markdown format — best for LLM consumption)
            text = doc.export_to_markdown() if hasattr(doc, "export_to_markdown") else str(doc)

            # TODO: Extract tables when owner approves full implementation
            return DocumentIntelligenceResult(
                text=text,
                engine_used=self.name,
                confidence=0.9,
                page_count=getattr(doc, "num_pages", 0),
                metadata={"format": "markdown", "source": file_path},
            )
        except Exception as e:
            logger.error(f"[DoclingEngine] Error: {e}")
            return DocumentIntelligenceResult.error_result(self.name, str(e))
