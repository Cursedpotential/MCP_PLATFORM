import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import http from "node:http";

/**
 * AI DIAL JavaScript MCP Server
 *
 * Houses legacy JS tools, Docling, and Pandoc wrappers.
 * Serves over HTTP (StreamableHTTPServerTransport) so DIAL Core and external
 * MCP clients can route requests to it.
 */

const PORT = parseInt(process.env.PORT || "8083", 10);

function createMcpServer() {
  const server = new Server(
    { name: "dial-js-core", version: "1.0.0" },
    { capabilities: { tools: {} } }
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
      {
        name: "ping_js_server",
        description: "Ping the JS MCP server to verify it is running within DIAL.",
        inputSchema: { type: "object", properties: {} },
      },
      // TODO: Add Docling document conversion tool
      // TODO: Add Pandoc format conversion tool
      // TODO: Add legacy JS extractor wrappers
    ],
  }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    switch (request.params.name) {
      case "ping_js_server":
        return { content: [{ type: "text", text: "Pong from dial-js-core!" }] };

      default:
        throw new Error(`Unknown tool: ${request.params.name}`);
    }
  });

  server.onerror = (error) => console.error("[MCP Error]", error);

  return server;
}

// ---------------------------------------------------------------------------
// Minimal HTTP server using Node's built-in http module
// (no express dep in this package — keeps it lean)
// ---------------------------------------------------------------------------
const httpServer = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);

  // Health check
  if (url.pathname === "/health" && req.method === "GET") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok", server: "dial-js-core", port: PORT }));
    return;
  }

  // MCP endpoint
  if (url.pathname === "/mcp") {
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    const body = chunks.length > 0 ? JSON.parse(Buffer.concat(chunks).toString()) : undefined;

    const mcpServer = createMcpServer();
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
    });
    await mcpServer.connect(transport);
    await transport.handleRequest(req, res, body);
    res.on("finish", () => mcpServer.close());
    return;
  }

  res.writeHead(404);
  res.end("Not found");
});

httpServer.listen(PORT, () => {
  console.log(`[dial-js-core] MCP HTTP server listening on port ${PORT}`);
});

process.on("SIGINT", () => {
  console.log("[dial-js-core] Shutting down...");
  httpServer.close();
  process.exit(0);
});
