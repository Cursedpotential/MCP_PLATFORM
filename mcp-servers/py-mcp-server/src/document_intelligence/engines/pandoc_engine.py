"""
Pandoc engine adapter.

Strengths: Format conversion king, 40+ input formats, deterministic, fast.
Best for: Format conversion (DOCX→MD, HTML→MD, EPUB→MD, etc.),
          clean text extraction from well-formed documents.

Reference: Alpha 1 has working Pandoc in server/mcp/plugins/document-processors.ts
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ..base import DocumentEngine
from ..models import DocumentIntelligenceResult, EngineCapability, CostTier, Locality

logger = logging.getLogger(__name__)


class PandocEngine(DocumentEngine):
    @property
    def name(self) -> str:
        return "pandoc"

    @property
    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability.FORMAT_CONVERSION,
            EngineCapability.CHUNKING,
        ]

    @property
    def supported_formats(self) -> list[str]:
        # Pandoc supports 40+ formats; listing common ones
        return [
            ".docx", ".odt", ".rtf", ".html", ".htm", ".md", ".rst",
            ".tex", ".epub", ".txt", ".pdf", ".pptx",
        ]

    @property
    def cost_tier(self) -> CostTier:
        return CostTier.FREE

    @property
    def locality(self) -> Locality:
        return Locality.LOCAL

    def is_available(self) -> bool:
        return shutil.which("pandoc") is not None

    def process(self, file_path: str, task: str, options: dict[str, Any] | None = None) -> DocumentIntelligenceResult:
        """Convert document to markdown using Pandoc."""
        opts = options or {}
        output_format = opts.get("output_format", "markdown")

        try:
            with tempfile.NamedTemporaryFile(
                suffix=".md", delete=False, mode="w"
            ) as tmp:
                tmp_path = tmp.name

            cmd = ["pandoc", file_path, "-o", tmp_path, "-t", output_format]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                return DocumentIntelligenceResult.error_result(
                    self.name,
                    f"Pandoc error (code {result.returncode}): {result.stderr.strip()}"
                )

            text = Path(tmp_path).read_text(encoding="utf-8")
            Path(tmp_path).unlink(missing_ok=True)

            return DocumentIntelligenceResult(
                text=text,
                engine_used=self.name,
                confidence=1.0,
                metadata={"output_format": output_format, "source": file_path},
            )
        except subprocess.TimeoutExpired:
            return DocumentIntelligenceResult.error_result(self.name, "Pandoc timed out (>60s)")
        except Exception as e:
            logger.error(f"[PandocEngine] Error: {e}")
            return DocumentIntelligenceResult.error_result(self.name, str(e))
