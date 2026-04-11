"""
DocTR engine adapter (Deep Learning OCR).

Strengths: Deep learning OCR, excellent on noisy/complex layouts,
real-world scans, non-standard fonts.
Best for: Messy scanned documents, photos of documents,
          low-quality images, real-world captures.

Note: Referred to as 'DocStrange' in early project notes — this is the doctr library.
"""

from __future__ import annotations

import logging
from typing import Any

from ..base import DocumentEngine
from ..models import DocumentIntelligenceResult, EngineCapability, CostTier, Locality

logger = logging.getLogger(__name__)


class DocTREngine(DocumentEngine):
    @property
    def name(self) -> str:
        return "doctr"

    @property
    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability.OCR,
            EngineCapability.LAYOUT_ANALYSIS,
        ]

    @property
    def supported_formats(self) -> list[str]:
        return [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"]

    @property
    def cost_tier(self) -> CostTier:
        return CostTier.FREE

    @property
    def locality(self) -> Locality:
        return Locality.LOCAL

    def is_available(self) -> bool:
        try:
            import doctr  # noqa: F401
            return True
        except ImportError:
            return False

    def process(self, file_path: str, task: str, options: dict[str, Any] | None = None) -> DocumentIntelligenceResult:
        """
        Process document using DocTR deep learning OCR.
        TODO: Full implementation requires owner approval.
        """
        try:
            from doctr.io import DocumentFile
            from doctr.models import ocr_predictor

            model = ocr_predictor(pretrained=True)
            doc = DocumentFile.from_images([file_path]) if not file_path.endswith(".pdf") else DocumentFile.from_pdf(file_path)
            result = model(doc)

            # Extract text from result structure
            text_parts = []
            for page in result.pages:
                for block in page.blocks:
                    for line in block.lines:
                        text_parts.append(" ".join(w.value for w in line.words))

            return DocumentIntelligenceResult(
                text="\n".join(text_parts),
                engine_used=self.name,
                confidence=0.85,
                page_count=len(result.pages),
                metadata={"source": file_path},
            )
        except Exception as e:
            logger.error(f"[DocTREngine] Error: {e}")
            return DocumentIntelligenceResult.error_result(self.name, str(e))
