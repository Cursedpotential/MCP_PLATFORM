# py-mcp-server (AI DIAL Stack)

## Architecture Overview
This directory contains the **Python MCP Server**, built with **FastMCP**. It interfaces directly with the AI DIAL orchestration framework.

This is part of **Sprint 1** to replace the monolithic, over-engineered memory service and TS coordinators. All state configuration and pipeline routing is handled natively by the DIAL core now. **This server only registers atomic, independent Python tools**.

## Purpose & Scope
This server wraps heavy-duty machine learning, vector logic, and graph computations into localized FastMCP endpoints.
It is restricted to the following responsibilities:

### 1. Vector Operations
*   LanceDB memory insertions
*   Semantica fact extraction/chunking logic

### 2. Graph Operations
*   Neo4j deep graph traversal/entity mapping

## AI Agent Handover Notes (Rate Limiting/New Sessions)
If you are a new agent taking over this project:
1.  **Strict Isolation**: This `py-mcp-server` subdirectory is completely pristine. **Do not** import scattered scripts directly from the fragmented D drive directories (`D:\AI_Workspace\Tools\...`).
2.  **No Monolithic Endpoints**: Previously, `memory_service.py` attempted to be a bulky FastApi memory manager. We are using FastMCP now. We define functions. We use the `@mcp.tool()` decorator.
3.  **To Add a Tool**: Write a standard Python function in `src/tools/` wrapping one of the legacy algorithms. Import it into `src/server.py`, run `mcp.add_tool()`, and DIAL will distribute it.

## Getting Started
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
fastmcp run src/server.py
```
