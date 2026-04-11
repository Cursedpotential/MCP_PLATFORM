"""
GLM-OCR engine adapter (CogVLM/GLM-4V based).

Strengths: Vision-language model OCR, understands context not just characters,
can describe what it sees.
Best for: Context-aware extraction, documents where understanding meaning matters,
mixed text+image content.

Can run locally with GPU or via API.
Env: GLM_OCR_ENDPOINT (default: http://localhost:8088), GLM_OCR_API_KEY (optional)

NOTE: Requires owner approval before enabling in any environment.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from ..base import DocumentEngine
from ..models import DocumentIntelligenceResult, EngineCapability, CostTier, Locality

logger = logging.getLogger(__name__)


class GlmOcrEngine(DocumentEngine):
    @property
    def name(self) -> str:
        return "glm_ocr"

    @property
    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability.OCR,
            EngineCapability.CONTEXT_AWARE,
            EngineCapability.MULTILINGUAL,
        ]

    @property
    def supported_formats(self) -> list[str]:
        return [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"]

    @property
    def cost_tier(self) -> CostTier:
        endpoint = os.getenv("GLM_OCR_ENDPOINT", "http://localhost:8088")
        return CostTier.FREE if "localhost" in endpoint else CostTier.PAID_PER_USE

    @property
    def locality(self) -> Locality:
        endpoint = os.getenv("GLM_OCR_ENDPOINT", "http://localhost:8088")
        return Locality.LOCAL if "localhost" in endpoint else Locality.CLOUD

    def is_available(self) -> bool:
        endpoint = os.getenv("GLM_OCR_ENDPOINT", "")
        if not endpoint:
            return False
        try:
            import requests
            resp = requests.get(f"{endpoint}/health", timeout=2)
            return resp.status_code == 200
        except Exception:
            return False

    def process(self, file_path: str, task: str, options: dict[str, Any] | None = None) -> DocumentIntelligenceResult:
        """
        Process document using GLM-OCR vision-language model.
        TODO: Full implementation requires owner approval + GLM endpoint setup.
        """
        try:
            import base64
            import requests

            endpoint = os.getenv("GLM_OCR_ENDPOINT", "http://localhost:8088")
            api_key = os.getenv("GLM_OCR_API_KEY", "")

            with open(file_path, "rb") as f:
                content_b64 = base64.b64encode(f.read()).decode()

            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            prompt = (options or {}).get("prompt", "Extract all text from this document. Preserve structure.")
            payload = {
                "image": content_b64,
                "prompt": prompt,
                "max_tokens": 4096,
            }

            resp = requests.post(f"{endpoint}/ocr", json=payload, headers=headers, timeout=120)
            resp.raise_for_status()
            data = resp.json()

            return DocumentIntelligenceResult(
                text=data.get("text", ""),
                engine_used=self.name,
                confidence=0.88,
                metadata={"endpoint": endpoint, "source": file_path},
            )
        except Exception as e:
            logger.error(f"[GlmOcrEngine] Error: {e}")
            return DocumentIntelligenceResult.error_result(self.name, str(e))
