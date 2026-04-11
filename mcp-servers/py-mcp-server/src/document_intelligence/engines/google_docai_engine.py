"""
Google Document AI engine adapter.

Strengths: Best handwriting recognition, excellent on low-res images,
200+ languages, pre-trained processors for invoices/contracts/IDs.
Best for: Handwritten notes/letters, multilingual documents,
identity documents, poor-quality scans.

Cloud-only. Requires GCP credentials:
  GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
  GOOGLE_DOCAI_PROJECT_ID=your-gcp-project-id
  GOOGLE_DOCAI_LOCATION=us

NOTE: Requires owner approval before enabling in any environment.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from ..base import DocumentEngine
from ..models import DocumentIntelligenceResult, EngineCapability, CostTier, Locality

logger = logging.getLogger(__name__)


class GoogleDocAIEngine(DocumentEngine):
    @property
    def name(self) -> str:
        return "google_docai"

    @property
    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability.OCR,
            EngineCapability.HANDWRITING,
            EngineCapability.MULTILINGUAL,
            EngineCapability.FORM_EXTRACTION,
            EngineCapability.TABLE_EXTRACTION,
        ]

    @property
    def supported_formats(self) -> list[str]:
        return [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".gif", ".bmp", ".webp"]

    @property
    def cost_tier(self) -> CostTier:
        return CostTier.PAID_PER_USE

    @property
    def locality(self) -> Locality:
        return Locality.CLOUD

    def is_available(self) -> bool:
        creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_DOCAI_PROJECT_ID")
        if not creds:
            return False
        try:
            from google.cloud import documentai  # noqa: F401
            return True
        except ImportError:
            return False

    def process(self, file_path: str, task: str, options: dict[str, Any] | None = None) -> DocumentIntelligenceResult:
        """
        Process document using Google Document AI.
        TODO: Full implementation requires owner approval + GCP setup.
        See: https://cloud.google.com/document-ai/docs/process-documents-client-libraries
        """
        try:
            from google.cloud import documentai
            from google.api_core.client_options import ClientOptions

            project_id = os.getenv("GOOGLE_DOCAI_PROJECT_ID", "")
            location = os.getenv("GOOGLE_DOCAI_LOCATION", "us")
            processor_id = (options or {}).get("processor_id", "")

            if not processor_id:
                return DocumentIntelligenceResult.error_result(
                    self.name, "options.processor_id is required for Google Document AI"
                )

            client = documentai.DocumentProcessorServiceClient(
                client_options=ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
            )
            name = client.processor_path(project_id, location, processor_id)

            with open(file_path, "rb") as f:
                content = f.read()

            import mimetypes
            mime_type = mimetypes.guess_type(file_path)[0] or "application/pdf"
            raw_document = documentai.RawDocument(content=content, mime_type=mime_type)
            request = documentai.ProcessRequest(name=name, raw_document=raw_document)
            result = client.process_document(request=request)

            return DocumentIntelligenceResult(
                text=result.document.text,
                engine_used=self.name,
                confidence=0.95,
                page_count=len(result.document.pages),
                metadata={"processor_id": processor_id, "source": file_path},
            )
        except Exception as e:
            logger.error(f"[GoogleDocAIEngine] Error: {e}")
            return DocumentIntelligenceResult.error_result(self.name, str(e))
