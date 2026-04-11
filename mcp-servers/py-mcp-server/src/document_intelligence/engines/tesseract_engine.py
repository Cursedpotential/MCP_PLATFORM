"""
Tesseract OCR engine adapter.

Strengths: Widest language support (100+ languages), fast, simple,
reliable for clean print.
Best for: Clean printed documents, multi-language OCR, batch processing.

Reference: Alpha 1 has working Tesseract in server/mcp/plugins/ocr.ts and document.ts
"""

from __future__ import annotations

import logging
import shutil
from typing import Any

from ..base import DocumentEngine
from ..models import DocumentIntelligenceResult, EngineCapability, CostTier, Locality

logger = logging.getLogger(__name__)


class TesseractEngine(DocumentEngine):
    @property
    def name(self) -> str:
        return "tesseract"

    @property
    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability.OCR,
            EngineCapability.MULTILINGUAL,
        ]

    @property
    def supported_formats(self) -> list[str]:
        return [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp", ".pdf"]

    @property
    def cost_tier(self) -> CostTier:
        return CostTier.FREE

    @property
    def locality(self) -> Locality:
        return Locality.LOCAL

    def is_available(self) -> bool:
        if shutil.which("tesseract") is None:
            return False
        try:
            import pytesseract  # noqa: F401
            return True
        except ImportError:
            return False

    def process(self, file_path: str, task: str, options: dict[str, Any] | None = None) -> DocumentIntelligenceResult:
        """
        Perform OCR using Tesseract via pytesseract.
        Reference: Alpha 1 server/mcp/plugins/ocr.ts for language configuration.
        """
        opts = options or {}
        lang = opts.get("lang", "eng")

        try:
            import pytesseract
            from PIL import Image

            if file_path.lower().endswith(".pdf"):
                # PDF: convert pages to images first
                try:
                    import pdf2image
                    images = pdf2image.convert_from_path(file_path)
                    texts = [pytesseract.image_to_string(img, lang=lang) for img in images]
                    text = "\n\n--- Page Break ---\n\n".join(texts)
                    page_count = len(images)
                except ImportError:
                    return DocumentIntelligenceResult.error_result(
                        self.name, "pdf2image required for PDF OCR — install with: pip install pdf2image"
                    )
            else:
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image, lang=lang)
                page_count = 1

            return DocumentIntelligenceResult(
                text=text,
                engine_used=self.name,
                confidence=0.8,
                page_count=page_count,
                metadata={"lang": lang, "source": file_path},
            )
        except Exception as e:
            logger.error(f"[TesseractEngine] Error: {e}")
            return DocumentIntelligenceResult.error_result(self.name, str(e))
