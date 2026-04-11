"""Shared data models for the document intelligence package."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class EngineCapability(str, Enum):
    OCR = "ocr"
    TABLE_EXTRACTION = "table_extraction"
    LAYOUT_ANALYSIS = "layout_analysis"
    FORMAT_CONVERSION = "format_conversion"
    CHUNKING = "chunking"
    HANDWRITING = "handwriting"
    MULTILINGUAL = "multilingual"
    FORM_EXTRACTION = "form_extraction"
    CONTEXT_AWARE = "context_aware"
    RAG_NATIVE = "rag_native"


class CostTier(str, Enum):
    FREE = "free"
    PAID_PER_USE = "paid_per_use"
    ENTERPRISE = "enterprise"


class Locality(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


@dataclass
class TableCell:
    row: int
    col: int
    text: str
    confidence: float = 1.0


@dataclass
class Table:
    rows: int
    cols: int
    cells: list[TableCell] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class DocumentIntelligenceResult:
    """Unified result from any document intelligence engine."""

    # Core output
    text: str = ""
    tables: list[Table] = field(default_factory=list)

    # Engine metadata
    engine_used: str = "unknown"
    processing_time_ms: float = 0.0

    # Quality indicators
    confidence: float = 0.0
    page_count: int = 0

    # Structured metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    # Error tracking
    success: bool = True
    error: Optional[str] = None

    @classmethod
    def error_result(cls, engine_used: str, error: str) -> "DocumentIntelligenceResult":
        return cls(success=False, engine_used=engine_used, error=error)
