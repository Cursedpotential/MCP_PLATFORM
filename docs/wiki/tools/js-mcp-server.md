---
title: JS MCP Server
reviewed: 2026-04-08
revision: 2
author: Codex
status: current
---

# JS MCP Server

## Overview

The JavaScript MCP server is still a placeholder service. It exposes one live health-style tool and leaves document-processing wrappers as TODO comments in the source.

Sources: `mcp-servers/js-mcp-server/src/index.js`

## Live Tool

- `ping_js_server`

Sources: `mcp-servers/js-mcp-server/src/index.js`

## Architecture Notes

- The server uses Node's built-in `http` module plus `StreamableHTTPServerTransport`.
- `/health` returns server status.
- `/mcp` instantiates a fresh MCP server per request.

Sources: `mcp-servers/js-mcp-server/src/index.js`

## Planned Space

The source file still carries TODOs for Docling conversion, Pandoc conversion, and legacy extractor wrappers. None of those tools are registered today.

Sources: `mcp-servers/js-mcp-server/src/index.js`

## Change Log

- 2026-04-08, rev 2, Codex: condensed the page to the real implemented state.
