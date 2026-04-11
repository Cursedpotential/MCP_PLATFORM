"""
LlamaParse engine adapter (LlamaIndex / LlamaCloud).

Strengths: RAG-native, designed for LLM ingestion, auto-routes pages to
cheapest sufficient tier, multimodal.
Best for: Building knowledge bases, document Q&A, chunking for RAG pipelines,
cost-optimized batch processing.

Cloud API. Requires: LLAMA_CLOUD_API_KEY

NOTE: Requires owner approval before enabling in any environment.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from ..base import DocumentEngine
from ..models import DocumentIntelligenceResult, EngineCapability, CostTier, Locality

logger = logging.getLogger(__name__)


class LlamaParseEngine(DocumentEngine):
    @property
    def name(self) -> str:
        return "llamaparse"

    @property
    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability.OCR,
            EngineCapability.TABLE_EXTRACTION,
            EngineCapability.CHUNKING,
            EngineCapability.RAG_NATIVE,
            EngineCapability.LAYOUT_ANALYSIS,
        ]

    @property
    def supported_formats(self) -> list[str]:
        return [".pdf", ".docx", ".html", ".pptx", ".png", ".jpg", ".jpeg"]

    @property
    def cost_tier(self) -> CostTier:
        return CostTier.PAID_PER_USE

    @property
    def locality(self) -> Locality:
        return Locality.CLOUD

    def is_available(self) -> bool:
        if not os.getenv("LLAMA_CLOUD_API_KEY"):
            return False
        try:
            import llama_parse  # noqa: F401
            return True
        except ImportError:
            return False

    def process(self, file_path: str, task: str, options: dict[str, Any] | None = None) -> DocumentIntelligenceResult:
        """
        Process document using LlamaParse.
        TODO: Full implementation requires owner approval + LLAMA_CLOUD_API_KEY.
        """
        try:
            from llama_parse import LlamaParse

            api_key = os.getenv("LLAMA_CLOUD_API_KEY", "")
            result_type = (options or {}).get("result_type", "markdown")

            parser = LlamaParse(api_key=api_key, result_type=result_type)
            documents = parser.load_data(file_path)

            text = "\n\n".join(doc.text for doc in documents if hasattr(doc, "text"))

            return DocumentIntelligenceResult(
                text=text,
                engine_used=self.name,
                confidence=0.92,
                page_count=len(documents),
                metadata={"result_type": result_type, "source": file_path},
            )
        except Exception as e:
            logger.error(f"[LlamaParseEngine] Error: {e}")
            return DocumentIntelligenceResult.error_result(self.name, str(e))
