"""
Central registry of all document processing engines.

Discovers available engines at runtime and recommends the best one for a task.
"""

from __future__ import annotations

import logging
from typing import Optional

from .base import DocumentEngine
from .models import EngineCapability, CostTier, Locality

logger = logging.getLogger(__name__)

# Task → preferred capabilities mapping
TASK_CAPABILITY_MAP: dict[str, EngineCapability] = {
    "ocr": EngineCapability.OCR,
    "table_extraction": EngineCapability.TABLE_EXTRACTION,
    "layout_analysis": EngineCapability.LAYOUT_ANALYSIS,
    "format_conversion": EngineCapability.FORMAT_CONVERSION,
    "chunking": EngineCapability.CHUNKING,
    "handwriting": EngineCapability.HANDWRITING,
    "multilingual": EngineCapability.MULTILINGUAL,
    "form_extraction": EngineCapability.FORM_EXTRACTION,
    "context_aware": EngineCapability.CONTEXT_AWARE,
    "rag_native": EngineCapability.RAG_NATIVE,
}

# Preference order: local free engines first, then paid cloud
LOCALITY_PREFERENCE = [Locality.LOCAL, Locality.HYBRID, Locality.CLOUD]
COST_PREFERENCE = [CostTier.FREE, CostTier.PAID_PER_USE, CostTier.ENTERPRISE]


class EngineRegistry:
    """Registry and recommender for document intelligence engines."""

    def __init__(self) -> None:
        self._engines: dict[str, DocumentEngine] = {}
        self._initialized = False

    def register(self, engine: DocumentEngine) -> None:
        """Register an engine instance."""
        self._engines[engine.name] = engine
        logger.debug(f"[EngineRegistry] Registered engine: {engine.name}")

    def get(self, name: str) -> Optional[DocumentEngine]:
        """Get a specific engine by name."""
        return self._engines.get(name)

    def list_all(self) -> list[dict]:
        """List all registered engines with their status."""
        return [e.describe() for e in self._engines.values()]

    def list_available(self) -> list[DocumentEngine]:
        """Return only engines that pass is_available() check."""
        return [e for e in self._engines.values() if e.is_available()]

    def recommend(
        self,
        task: str,
        file_extension: str = "",
        prefer_local: bool = True,
    ) -> Optional[DocumentEngine]:
        """
        Recommend the best available engine for a given task and file type.

        Preference order:
        1. Supports the required capability
        2. Supports the file extension
        3. Local > Cloud (if prefer_local)
        4. Free > Paid > Enterprise

        Returns None if no suitable engine is available.
        """
        capability = TASK_CAPABILITY_MAP.get(task)
        ext = file_extension.lower()

        candidates = [
            e for e in self.list_available()
            if (capability is None or capability in e.capabilities)
            and (not ext or ext in e.supported_formats or not e.supported_formats)
        ]

        if not candidates:
            return None

        def sort_key(engine: DocumentEngine):
            loc_score = LOCALITY_PREFERENCE.index(engine.locality) if engine.locality in LOCALITY_PREFERENCE else 99
            cost_score = COST_PREFERENCE.index(engine.cost_tier) if engine.cost_tier in COST_PREFERENCE else 99
            if not prefer_local:
                loc_score = 0  # Ignore locality preference
            return (loc_score, cost_score)

        return sorted(candidates, key=sort_key)[0]

    def build_fallback_chain(self, task: str, file_extension: str = "") -> list[DocumentEngine]:
        """
        Build an ordered fallback chain for a task.
        Returns engines sorted by preference (best first).
        """
        capability = TASK_CAPABILITY_MAP.get(task)
        ext = file_extension.lower()

        candidates = [
            e for e in self.list_available()
            if (capability is None or capability in e.capabilities)
            and (not ext or ext in e.supported_formats or not e.supported_formats)
        ]

        def sort_key(engine: DocumentEngine):
            loc_score = LOCALITY_PREFERENCE.index(engine.locality) if engine.locality in LOCALITY_PREFERENCE else 99
            cost_score = COST_PREFERENCE.index(engine.cost_tier) if engine.cost_tier in COST_PREFERENCE else 99
            return (loc_score, cost_score)

        return sorted(candidates, key=sort_key)


# ---------------------------------------------------------------------------
# Module-level singleton — lazy initialization
# ---------------------------------------------------------------------------
_registry: Optional[EngineRegistry] = None


def get_registry() -> EngineRegistry:
    """Get or create the global engine registry, loading all engine adapters."""
    global _registry
    if _registry is not None:
        return _registry

    _registry = EngineRegistry()

    # Import and register all engines (each handles its own availability check)
    from .engines.docling_engine import DoclingEngine
    from .engines.pandoc_engine import PandocEngine
    from .engines.doctr_engine import DocTREngine
    from .engines.tesseract_engine import TesseractEngine
    from .engines.google_docai_engine import GoogleDocAIEngine
    from .engines.aws_textract_engine import AwsTextractEngine
    from .engines.glm_ocr_engine import GlmOcrEngine
    from .engines.llamaparse_engine import LlamaParseEngine
    from .engines.ocropus_engine import OcropusEngine
    from .engines.unstructured_engine import UnstructuredEngine
    from .engines.ibm_watsonx_engine import IbmWatsonxEngine

    for engine_cls in [
        DoclingEngine, PandocEngine, DocTREngine, TesseractEngine,
        GoogleDocAIEngine, AwsTextractEngine, GlmOcrEngine, LlamaParseEngine,
        OcropusEngine, UnstructuredEngine, IbmWatsonxEngine,
    ]:
        try:
            _registry.register(engine_cls())
        except Exception as e:
            logger.warning(f"[EngineRegistry] Failed to load {engine_cls.__name__}: {e}")

    logger.info(f"[EngineRegistry] Loaded {len(_registry._engines)} engines")
    return _registry
