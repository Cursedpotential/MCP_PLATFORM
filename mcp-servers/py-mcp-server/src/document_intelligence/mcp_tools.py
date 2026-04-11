"""
MCP tool registrations for the document intelligence package.

Registers 6 tools with the py-mcp-server FastMCP instance.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def register_document_intelligence_tools(mcp) -> None:
    """Register all document intelligence MCP tools with a FastMCP instance."""

    @mcp.tool()
    def document_process(
        file_path: str,
        task: str = "ocr",
        engine: Optional[str] = None,
        options_json: Optional[str] = None,
        prefer_local: bool = True,
    ) -> str:
        """
        Process a document with intelligent engine routing.

        Args:
            file_path: Absolute path to the document.
            task: Processing task — one of: ocr, table_extraction, layout_analysis,
                  format_conversion, chunking, handwriting, multilingual, form_extraction
            engine: Optional explicit engine name (auto-selects if not provided).
            options_json: Optional JSON string of engine-specific options.
            prefer_local: Prefer local engines over cloud (default: true).

        Returns:
            JSON DocumentIntelligenceResult.
        """
        from .router import DocumentRouter

        options = json.loads(options_json) if options_json else None
        router = DocumentRouter()
        result = router.route(file_path, task, engine_name=engine, options=options, prefer_local=prefer_local)
        return json.dumps({
            "success": result.success,
            "engine_used": result.engine_used,
            "text": result.text,
            "page_count": result.page_count,
            "confidence": result.confidence,
            "processing_time_ms": result.processing_time_ms,
            "metadata": result.metadata,
            "error": result.error,
        }, indent=2)

    @mcp.tool()
    def document_ocr(
        file_path: str,
        engine: Optional[str] = None,
        lang: str = "eng",
    ) -> str:
        """
        OCR a document with engine selection (auto or explicit).

        Args:
            file_path: Absolute path to the image or PDF.
            engine: Optional explicit engine name (auto-selects best available OCR engine).
            lang: Language hint for OCR engines that support it (default: eng).

        Returns:
            JSON DocumentIntelligenceResult.
        """
        from .router import DocumentRouter

        router = DocumentRouter()
        result = router.route(file_path, "ocr", engine_name=engine, options={"lang": lang})
        return json.dumps({
            "success": result.success,
            "engine_used": result.engine_used,
            "text": result.text,
            "confidence": result.confidence,
            "processing_time_ms": result.processing_time_ms,
            "error": result.error,
        }, indent=2)

    @mcp.tool()
    def document_convert(
        file_path: str,
        output_format: str = "markdown",
        engine: Optional[str] = None,
    ) -> str:
        """
        Convert a document to another format (routes to Pandoc primarily).

        Args:
            file_path: Absolute path to the document.
            output_format: Target format (default: markdown). Also: html, rst, latex, docx.
            engine: Optional explicit engine name.

        Returns:
            JSON DocumentIntelligenceResult with converted text.
        """
        from .router import DocumentRouter

        router = DocumentRouter()
        result = router.route(
            file_path, "format_conversion",
            engine_name=engine or "pandoc",
            options={"output_format": output_format}
        )
        return json.dumps({
            "success": result.success,
            "engine_used": result.engine_used,
            "text": result.text,
            "processing_time_ms": result.processing_time_ms,
            "error": result.error,
        }, indent=2)

    @mcp.tool()
    def document_extract_tables(
        file_path: str,
        engine: Optional[str] = None,
    ) -> str:
        """
        Extract tables from a document (routes to best available table engine).

        Args:
            file_path: Absolute path to the document (PDF, DOCX, or image).
            engine: Optional explicit engine name (auto-selects best table extractor).

        Returns:
            JSON DocumentIntelligenceResult with tables array.
        """
        from .router import DocumentRouter

        router = DocumentRouter()
        result = router.route(file_path, "table_extraction", engine_name=engine)
        return json.dumps({
            "success": result.success,
            "engine_used": result.engine_used,
            "text": result.text,
            "tables": [
                {
                    "rows": t.rows,
                    "cols": t.cols,
                    "confidence": t.confidence,
                    "cells": [{"row": c.row, "col": c.col, "text": c.text} for c in t.cells],
                }
                for t in result.tables
            ],
            "processing_time_ms": result.processing_time_ms,
            "error": result.error,
        }, indent=2)

    @mcp.tool()
    def document_engines_list() -> str:
        """
        List all registered document intelligence engines and their status.

        Returns:
            JSON array of engine descriptors with availability status.
        """
        from .engine_registry import get_registry

        registry = get_registry()
        engines = registry.list_all()
        return json.dumps({"engines": engines, "count": len(engines)}, indent=2)

    @mcp.tool()
    def document_engines_recommend(
        file_path: str,
        task: str = "ocr",
        prefer_local: bool = True,
    ) -> str:
        """
        Given a file and task, recommend which engine to use.

        Args:
            file_path: Path to the file (used for extension detection).
            task: Processing task.
            prefer_local: Prefer local engines (default: true).

        Returns:
            JSON with recommended engine and fallback chain.
        """
        import os as _os
        from .engine_registry import get_registry

        ext = _os.path.splitext(file_path)[1].lower()
        registry = get_registry()

        recommended = registry.recommend(task, ext, prefer_local=prefer_local)
        fallback_chain = registry.build_fallback_chain(task, ext)

        return json.dumps({
            "file": file_path,
            "extension": ext,
            "task": task,
            "recommended": recommended.describe() if recommended else None,
            "fallback_chain": [e.describe() for e in fallback_chain],
        }, indent=2)
