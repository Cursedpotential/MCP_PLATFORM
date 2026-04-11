"""
Unstructured library engine adapter.

Strengths: 65+ file types, excellent chunking for LLM/RAG,
partition-based approach, powerful connectors.
Best for: Multi-format ingestion pipelines, LLM-ready chunking,
email/HTML/mixed format processing.

Reference: Alpha 1 has working Unstructured in server/python-tools/unstructured_parser.py
"""

from __future__ import annotations

import logging
from typing import Any

from ..base import DocumentEngine
from ..models import DocumentIntelligenceResult, EngineCapability, CostTier, Locality

logger = logging.getLogger(__name__)


class UnstructuredEngine(DocumentEngine):
    @property
    def name(self) -> str:
        return "unstructured"

    @property
    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability.OCR,
            EngineCapability.CHUNKING,
            EngineCapability.LAYOUT_ANALYSIS,
            EngineCapability.RAG_NATIVE,
            EngineCapability.FORM_EXTRACTION,
        ]

    @property
    def supported_formats(self) -> list[str]:
        # Unstructured supports 65+ formats
        return [
            ".pdf", ".docx", ".doc", ".odt", ".rtf",
            ".html", ".htm", ".eml", ".msg",
            ".png", ".jpg", ".jpeg", ".tiff",
            ".txt", ".md", ".csv", ".xlsx", ".pptx",
        ]

    @property
    def cost_tier(self) -> CostTier:
        return CostTier.FREE

    @property
    def locality(self) -> Locality:
        return Locality.LOCAL

    def is_available(self) -> bool:
        try:
            from unstructured.partition.auto import partition  # noqa: F401
            return True
        except ImportError:
            return False

    def process(self, file_path: str, task: str, options: dict[str, Any] | None = None) -> DocumentIntelligenceResult:
        """
        Process document using Unstructured library.
        Reference: Alpha 1 server/python-tools/unstructured_parser.py
        TODO: Port chunking strategy from Alpha 1 when owner approves.
        """
        try:
            from unstructured.partition.auto import partition

            elements = partition(filename=file_path)
            text = "\n\n".join(str(el) for el in elements)

            return DocumentIntelligenceResult(
                text=text,
                engine_used=self.name,
                confidence=0.88,
                metadata={
                    "element_count": len(elements),
                    "element_types": list({type(el).__name__ for el in elements}),
                    "source": file_path,
                },
            )
        except Exception as e:
            logger.error(f"[UnstructuredEngine] Error: {e}")
            return DocumentIntelligenceResult.error_result(self.name, str(e))
