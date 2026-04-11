"""Abstract base class for all document intelligence engines."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

from .models import DocumentIntelligenceResult, EngineCapability, CostTier, Locality


class DocumentEngine(ABC):
    """
    Abstract base for all document processing engines.

    Every engine must implement:
    - name: str property
    - capabilities: list of EngineCapability
    - supported_formats: list of file extensions (e.g., ['.pdf', '.png'])
    - cost_tier: CostTier
    - locality: Locality
    - is_available() -> bool: runtime availability check
    - process(file_path, task, options) -> DocumentIntelligenceResult
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique engine identifier."""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> list[EngineCapability]:
        """List of tasks this engine can perform."""
        ...

    @property
    @abstractmethod
    def supported_formats(self) -> list[str]:
        """File extensions this engine can handle (lowercase, with dot)."""
        ...

    @property
    @abstractmethod
    def cost_tier(self) -> CostTier:
        """Cost classification for this engine."""
        ...

    @property
    @abstractmethod
    def locality(self) -> Locality:
        """Where this engine runs (local/cloud/hybrid)."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check whether this engine is available at runtime.
        Should check: package installed, credentials set, service reachable.
        """
        ...

    @abstractmethod
    def process(
        self,
        file_path: str,
        task: str,
        options: dict[str, Any] | None = None,
    ) -> DocumentIntelligenceResult:
        """
        Process a document file with this engine.

        Args:
            file_path: Absolute path to the document.
            task: One of: ocr, table_extraction, layout_analysis,
                  format_conversion, chunking, handwriting, multilingual,
                  form_extraction
            options: Engine-specific options dict.

        Returns:
            DocumentIntelligenceResult with unified output.
        """
        ...

    def _timed_process(
        self,
        file_path: str,
        task: str,
        options: dict[str, Any] | None = None,
    ) -> DocumentIntelligenceResult:
        """Wrapper that adds processing_time_ms to any engine."""
        start = time.perf_counter()
        result = self.process(file_path, task, options)
        result.processing_time_ms = (time.perf_counter() - start) * 1000
        return result

    def describe(self) -> dict[str, Any]:
        """Return a JSON-serializable description of this engine."""
        return {
            "name": self.name,
            "capabilities": [c.value for c in self.capabilities],
            "supported_formats": self.supported_formats,
            "cost_tier": self.cost_tier.value,
            "locality": self.locality.value,
            "available": self.is_available(),
        }
