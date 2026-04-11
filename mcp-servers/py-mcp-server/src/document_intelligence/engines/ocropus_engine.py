"""
OCRopus engine adapter.

Strengths: Modular research pipeline, fully customizable,
trainable on domain-specific fonts/layouts.
Best for: Domain-specific OCR (historical documents, specialized fonts),
research/academic use, custom training.

Local-only. Requires setup: pip install ocropy (or ocropus-git)

NOTE: Requires owner approval before enabling in any environment.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ..base import DocumentEngine
from ..models import DocumentIntelligenceResult, EngineCapability, CostTier, Locality

logger = logging.getLogger(__name__)


class OcropusEngine(DocumentEngine):
    @property
    def name(self) -> str:
        return "ocropus"

    @property
    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability.OCR,
            EngineCapability.LAYOUT_ANALYSIS,
        ]

    @property
    def supported_formats(self) -> list[str]:
        return [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]

    @property
    def cost_tier(self) -> CostTier:
        return CostTier.FREE

    @property
    def locality(self) -> Locality:
        return Locality.LOCAL

    def is_available(self) -> bool:
        return (
            shutil.which("ocropus-nlbin") is not None
            or shutil.which("ocropus-gpageseg") is not None
        )

    def process(self, file_path: str, task: str, options: dict[str, Any] | None = None) -> DocumentIntelligenceResult:
        """
        Process image using OCRopus pipeline.
        TODO: Full pipeline (binarize → segment → recognize) requires owner approval.
        """
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Step 1: Binarize
                result = subprocess.run(
                    ["ocropus-nlbin", file_path, "-o", tmpdir],
                    capture_output=True, text=True, timeout=120
                )
                if result.returncode != 0:
                    return DocumentIntelligenceResult.error_result(
                        self.name, f"ocropus-nlbin failed: {result.stderr}"
                    )

                # TODO: Full segment + recognize pipeline
                # For now, return basic result indicating binarization succeeded
                return DocumentIntelligenceResult(
                    text="[OCRopus: binarization complete — full recognition pipeline requires owner approval]",
                    engine_used=self.name,
                    confidence=0.5,
                    metadata={"stage": "binarized", "source": file_path},
                )
        except subprocess.TimeoutExpired:
            return DocumentIntelligenceResult.error_result(self.name, "OCRopus timed out")
        except Exception as e:
            logger.error(f"[OcropusEngine] Error: {e}")
            return DocumentIntelligenceResult.error_result(self.name, str(e))
