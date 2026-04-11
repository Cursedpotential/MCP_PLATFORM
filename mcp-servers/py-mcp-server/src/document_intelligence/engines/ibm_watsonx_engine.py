"""
IBM Watson Document Understanding (watsonx.ai) engine adapter.

Strengths: Enterprise NLP, compliance, document structuring,
semantic classification, retention/redaction.
Best for: Regulated industries, legal documents, compliance workflows,
enterprise document management.

Cloud API, enterprise pricing.
Env: WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_URL

NOTE: Requires owner approval before enabling in any environment.
Enterprise license required.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from ..base import DocumentEngine
from ..models import DocumentIntelligenceResult, EngineCapability, CostTier, Locality

logger = logging.getLogger(__name__)


class IbmWatsonxEngine(DocumentEngine):
    @property
    def name(self) -> str:
        return "ibm_watsonx"

    @property
    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability.OCR,
            EngineCapability.LAYOUT_ANALYSIS,
            EngineCapability.FORM_EXTRACTION,
            EngineCapability.TABLE_EXTRACTION,
            EngineCapability.CONTEXT_AWARE,
        ]

    @property
    def supported_formats(self) -> list[str]:
        return [".pdf", ".docx", ".html", ".txt"]

    @property
    def cost_tier(self) -> CostTier:
        return CostTier.ENTERPRISE

    @property
    def locality(self) -> Locality:
        return Locality.CLOUD

    def is_available(self) -> bool:
        has_creds = bool(os.getenv("WATSONX_API_KEY") and os.getenv("WATSONX_PROJECT_ID"))
        if not has_creds:
            return False
        try:
            from ibm_watsonx_ai import APIClient  # noqa: F401
            return True
        except ImportError:
            return False

    def process(self, file_path: str, task: str, options: dict[str, Any] | None = None) -> DocumentIntelligenceResult:
        """
        Process document using IBM watsonx.ai Document Understanding.
        TODO: Full implementation requires owner approval + enterprise license.
        See: https://ibm.github.io/watsonx-ai-python-sdk/
        """
        try:
            from ibm_watsonx_ai import APIClient, Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference

            credentials = Credentials(
                api_key=os.getenv("WATSONX_API_KEY", ""),
                url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
            )
            project_id = os.getenv("WATSONX_PROJECT_ID", "")

            # TODO: Use Watson Document Understanding API for proper extraction
            # For now, use foundation model text extraction as placeholder
            client = APIClient(credentials=credentials)
            model = ModelInference(
                model_id="ibm/granite-13b-instruct-v2",
                api_client=client,
                project_id=project_id,
            )

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()[:10000]  # Limit for MVP

            response = model.generate_text(
                prompt=f"Extract and structure all text from this document:\n\n{content}"
            )

            return DocumentIntelligenceResult(
                text=response,
                engine_used=self.name,
                confidence=0.9,
                metadata={"project_id": project_id, "source": file_path},
            )
        except Exception as e:
            logger.error(f"[IbmWatsonxEngine] Error: {e}")
            return DocumentIntelligenceResult.error_result(self.name, str(e))
