"""
AWS Textract engine adapter.

Strengths: Industry-best table extraction with cell relationships,
key-value pair extraction, form understanding.
Best for: Forms, invoices, financial documents, complex nested tables, receipts.

Cloud-only. Requires AWS credentials:
  AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION

NOTE: Requires owner approval before enabling in any environment.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from ..base import DocumentEngine
from ..models import DocumentIntelligenceResult, EngineCapability, CostTier, Locality, Table, TableCell

logger = logging.getLogger(__name__)


class AwsTextractEngine(DocumentEngine):
    @property
    def name(self) -> str:
        return "aws_textract"

    @property
    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability.OCR,
            EngineCapability.TABLE_EXTRACTION,
            EngineCapability.FORM_EXTRACTION,
        ]

    @property
    def supported_formats(self) -> list[str]:
        return [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]

    @property
    def cost_tier(self) -> CostTier:
        return CostTier.PAID_PER_USE

    @property
    def locality(self) -> Locality:
        return Locality.CLOUD

    def is_available(self) -> bool:
        has_creds = bool(os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE"))
        if not has_creds:
            return False
        try:
            import boto3  # noqa: F401
            return True
        except ImportError:
            return False

    def process(self, file_path: str, task: str, options: dict[str, Any] | None = None) -> DocumentIntelligenceResult:
        """
        Process document using AWS Textract.
        TODO: Full table cell relationship extraction requires owner approval.
        """
        try:
            import boto3

            region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            client = boto3.client("textract", region_name=region)

            with open(file_path, "rb") as f:
                content = f.read()

            feature_types = ["TABLES", "FORMS"] if task in ("table_extraction", "form_extraction") else []
            if feature_types:
                response = client.analyze_document(
                    Document={"Bytes": content},
                    FeatureTypes=feature_types,
                )
            else:
                response = client.detect_document_text(Document={"Bytes": content})

            # Extract text from LINE blocks
            text_parts = [
                block["Text"]
                for block in response.get("Blocks", [])
                if block["BlockType"] == "LINE" and "Text" in block
            ]

            return DocumentIntelligenceResult(
                text="\n".join(text_parts),
                engine_used=self.name,
                confidence=0.92,
                metadata={"features": feature_types, "source": file_path},
            )
        except Exception as e:
            logger.error(f"[AwsTextractEngine] Error: {e}")
            return DocumentIntelligenceResult.error_result(self.name, str(e))
