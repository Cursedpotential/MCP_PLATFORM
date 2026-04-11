"""
Intelligent routing layer for document intelligence.

Routes processing requests to the best available engine, with fallback chains.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

from .engine_registry import EngineRegistry, get_registry
from .models import DocumentIntelligenceResult

logger = logging.getLogger(__name__)


class DocumentRouter:
    """
    Routes document processing requests to the appropriate engine.

    Supports:
    - Auto-selection based on task + file type
    - Explicit engine selection
    - Fallback chains (try best → fallback → fallback)
    """

    def __init__(self, registry: Optional[EngineRegistry] = None) -> None:
        self._registry = registry

    @property
    def registry(self) -> EngineRegistry:
        if self._registry is None:
            self._registry = get_registry()
        return self._registry

    def route(
        self,
        file_path: str,
        task: str,
        engine_name: Optional[str] = None,
        options: Optional[dict[str, Any]] = None,
        prefer_local: bool = True,
    ) -> DocumentIntelligenceResult:
        """
        Route a document processing request.

        Args:
            file_path: Absolute path to the document.
            task: Processing task (ocr, table_extraction, layout_analysis,
                  format_conversion, chunking, handwriting, multilingual,
                  form_extraction)
            engine_name: Optional explicit engine name. If None, auto-selects.
            options: Engine-specific options.
            prefer_local: If True, prefer local engines over cloud (default: True).

        Returns:
            DocumentIntelligenceResult from the engine that ran.
        """
        if not os.path.exists(file_path):
            return DocumentIntelligenceResult.error_result(
                engine_used="router",
                error=f"File not found: {file_path}",
            )

        file_ext = os.path.splitext(file_path)[1].lower()

        # Explicit engine selection
        if engine_name:
            engine = self.registry.get(engine_name)
            if engine is None:
                return DocumentIntelligenceResult.error_result(
                    engine_used=engine_name,
                    error=f"Engine '{engine_name}' not registered.",
                )
            if not engine.is_available():
                return DocumentIntelligenceResult.error_result(
                    engine_used=engine_name,
                    error=f"Engine '{engine_name}' is not available (missing deps or credentials).",
                )
            return engine._timed_process(file_path, task, options)

        # Auto-selection with fallback chain
        fallback_chain = self.registry.build_fallback_chain(task, file_ext)
        if not fallback_chain:
            return DocumentIntelligenceResult.error_result(
                engine_used="router",
                error=f"No available engine can handle task='{task}' for file type '{file_ext}'.",
            )

        last_error = "No engines tried"
        for engine in fallback_chain:
            try:
                result = engine._timed_process(file_path, task, options)
                if result.success:
                    logger.info(f"[Router] {task} on {file_ext} → {engine.name} (success)")
                    return result
                last_error = result.error or "Unknown failure"
                logger.warning(f"[Router] {engine.name} failed: {last_error}, trying next...")
            except Exception as e:
                last_error = str(e)
                logger.warning(f"[Router] {engine.name} raised exception: {e}, trying next...")

        return DocumentIntelligenceResult.error_result(
            engine_used="router",
            error=f"All engines failed for task='{task}'. Last error: {last_error}",
        )
