"""
Document Intelligence Package — Multi-Engine Document Processing Router

Provides a pluggable document processing layer where each engine is used
for what it's best at. NOT a monolithic OCR tool — an intelligent router.

NOTE: This package is a PLANNING/ARCHITECTURE implementation.
Nothing here is authorization to activate cloud engines in production.
Each engine activation requires explicit owner approval.
"""

from .models import DocumentIntelligenceResult, EngineCapability, CostTier, Locality
from .base import DocumentEngine
from .engine_registry import EngineRegistry
from .router import DocumentRouter

__all__ = [
    "DocumentIntelligenceResult",
    "EngineCapability",
    "CostTier",
    "Locality",
    "DocumentEngine",
    "EngineRegistry",
    "DocumentRouter",
]
