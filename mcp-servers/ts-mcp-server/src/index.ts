import express from "express";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from 'zod';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { SmsXmlParser } from "./tools/SmsXmlParser.js";
import { FacebookExportParser } from "./tools/FacebookExportParser.js";
import { ImessagePdfParser } from "./tools/ImessagePdfParser.js";
import { DuckDbVault } from "./tools/DuckDbVault.js";
import { PostgresWriter } from "./tools/PostgresWriter.js";
import { AdminTools } from "./tools/AdminTools.js";
import { ReviewQueue } from "./tools/ReviewQueue.js";
import { EvidenceIngestor } from "./tools/EvidenceIngestor.js";
import { Pass1Runner } from "./tools/Pass1Runner.js";
import { SbvClient } from "./tools/SbvClient.js";
import { SbvIngestor } from "./tools/SbvIngestor.js";

/**
 * AI DIAL TypeScript MCP Server
 *
 * Serves over HTTP (StreamableHTTPServerTransport) so AI DIAL Core can
 * route requests to it via the /mcp/chat/completions endpoint in config.json.
 *
 * Previously used StdioServerTransport — switched to HTTP for DIAL compatibility.
 */

const PORT = parseInt(process.env.PORT || "8081", 10);

// ---------------------------------------------------------------------------
// Lazy singletons — one shared instance per process, not per request
// ---------------------------------------------------------------------------
let _vault: DuckDbVault | null = null;
let _pg: PostgresWriter | null = null;
let _admin: AdminTools | null = null;
let _review: ReviewQueue | null = null;

function getVault(): DuckDbVault {
  if (!_vault) _vault = new DuckDbVault();
  return _vault;
}

function getPg(): PostgresWriter {
  if (!_pg) _pg = new PostgresWriter();
  return _pg;
}

function getAdmin(): AdminTools {
  if (!_admin) _admin = new AdminTools();
  return _admin;
}

function getReview(): ReviewQueue {
  if (!_review) _review = new ReviewQueue();
  return _review;
}

let _ingestor: EvidenceIngestor | null = null;
let _pass1: Pass1Runner | null = null;

function getIngestor(): EvidenceIngestor {
  if (!_ingestor) _ingestor = new EvidenceIngestor(getVault(), getPg());
  return _ingestor;
}

function getPass1(): Pass1Runner {
  if (!_pass1) _pass1 = new Pass1Runner(getVault(), getPg());
  return _pass1;
}

let _sbvClient: SbvClient | null = null;
let _sbvIngestor: SbvIngestor | null = null;

function getSbvClient(): SbvClient {
  if (!_sbvClient) _sbvClient = new SbvClient();
  return _sbvClient;
}

function getSbvIngestor(): SbvIngestor {
  if (!_sbvIngestor) _sbvIngestor = new SbvIngestor(getVault(), getPg(), getSbvClient());
  return _sbvIngestor;
}

// ---------------------------------------------------------------------------
// Build and attach the MCP Server
// ---------------------------------------------------------------------------
function createMcpServer(): Server {
  const server = new Server(
    { name: "dial-ts-core", version: "1.0.0" },
    { capabilities: { tools: {} } }
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
      {
        name: "ping",
        description: "Ping the TS MCP server to verify it is running within DIAL",
        inputSchema: { type: "object", properties: {} },
      },
      {
        name: "parse_sms_xml",
        description: "Parses massive SMS/Call Backup XML files into normalized JSON arrays.",
        inputSchema: {
          type: "object",
          properties: {
            file_path: { type: "string", description: "Absolute file path to the XML file." },
          },
          required: ["file_path"],
        },
      },
      {
        name: "parse_facebook_export",
        description: "Parses Facebook Messenger HTML/JSON export files into normalized JSON arrays.",
        inputSchema: {
          type: "object",
          properties: {
            file_path: { type: "string", description: "Absolute file path to the HTML/JSON file." },
            own_name: { type: "string", description: "Optional. Your name, to determine inbound/outbound direction." },
          },
          required: ["file_path"],
        },
      },
      {
        name: "parse_imessage_pdf",
        description: "Parses iMessage PDF exports into normalized JSON arrays.",
        inputSchema: {
          type: "object",
          properties: {
            file_path: { type: "string", description: "Absolute file path to the PDF file." },
          },
          required: ["file_path"],
        },
      },
      {
        name: "vault_log_ingestion",
        description: "Logs a new file into the forensic DuckDB vault with SHA-256 chain of custody.",
        inputSchema: {
          type: "object",
          properties: {
            source_type: { type: "string" },
            source_name: { type: "string" },
            raw_content: { type: "string" },
            binary_path: { type: "string" },
          },
          required: ["source_type", "source_name"],
        },
      },
      {
        name: "vault_get_pending_pass1",
        description: "Gets ingested files pending Pass 1 enrichment (embedding).",
        inputSchema: { type: "object", properties: {} },
      },
      {
        name: "vault_update_pass1_status",
        description: "Updates the Pass 1 status for a file in the DuckDB vault.",
        inputSchema: {
          type: "object",
          properties: {
            ingestion_id: { type: "string" },
            status: { type: "string", enum: ["pending", "processing", "completed", "failed"] },
          },
          required: ["ingestion_id", "status"],
        },
      },
      {
        name: "vault_update_write_tracking",
        description: "Records that a file has been written to a specific storage tier.",
        inputSchema: {
          type: "object",
          properties: {
            ingestion_id: { type: "string" },
            tier: { type: "string", enum: ["lancedb", "neo4j_semantic", "neo4j_temporal", "postgresql"] },
            written: { type: "boolean" },
          },
          required: ["ingestion_id", "tier", "written"],
        },
      },
      {
        name: "postgres_write_record",
        description: "Inserts a structured row into the unified PostgreSQL evidence or app tier.",
        inputSchema: {
          type: "object",
          properties: {
            table_name: { type: "string" },
            data: { type: "object", description: "Key-value pairs to insert." },
          },
          required: ["table_name", "data"],
        },
      },
      {
        name: "postgres_raw_query",
        description: "Executes a read-only SELECT query against PostgreSQL. Non-SELECT statements (INSERT, UPDATE, DELETE, DROP) are blocked. Use postgres_write_record for writes.",
        inputSchema: {
          type: "object",
          properties: {
            sql: { type: "string", description: "Parameterized SQL query." },
            params: { type: "array", description: "Query parameters array (avoids SQL injection).", items: {} },
          },
          required: ["sql"],
        },
      },
      // Admin Tools
      {
        name: "admin_list_llm_providers",
        description: "Lists all configured LLM providers from the app tier.",
        inputSchema: { type: "object", properties: {} },
      },
      {
        name: "admin_upsert_llm_provider",
        description: "Adds or updates an LLM provider configuration.",
        inputSchema: {
          type: "object",
          properties: {
            provider_name: { type: "string" },
            api_key_encrypted: { type: "string" },
            base_url: { type: "string" },
            is_active: { type: "boolean" },
            priority: { type: "integer" },
          },
          required: ["provider_name", "api_key_encrypted"],
        },
      },
      {
        name: "admin_list_system_prompts",
        description: "Lists all system prompts and their versions.",
        inputSchema: { type: "object", properties: {} },
      },
      {
        name: "admin_upsert_system_prompt",
        description: "Adds a new version of a system prompt.",
        inputSchema: {
          type: "object",
          properties: {
            name: { type: "string" },
            description: { type: "string" },
            tool_name: { type: "string" },
            prompt_text: { type: "string" },
            variables: { type: "object" },
          },
          required: ["name", "prompt_text"],
        },
      },
      // Review Queue (HITL)
      {
        name: "review_list_pending",
        description: "Lists items pending human review (entity merges, classifications, etc).",
        inputSchema: {
          type: "object",
          properties: { limit: { type: "integer", default: 50 } },
        },
      },
      {
        name: "review_approve",
        description: "Approves a review item, marking it for commitment.",
        inputSchema: {
          type: "object",
          properties: {
            id: { type: "string" },
            reviewed_by: { type: "string" },
            notes: { type: "string" },
          },
          required: ["id", "reviewed_by"],
        },
      },
      {
        name: "review_reject",
        description: "Rejects a review item.",
        inputSchema: {
          type: "object",
          properties: {
            id: { type: "string" },
            reviewed_by: { type: "string" },
            notes: { type: "string" },
          },
          required: ["id", "reviewed_by"],
        },
      },
      {
        name: "review_submit",
        description: "Submits an AI result for human review.",
        inputSchema: {
          type: "object",
          properties: {
            review_type: { type: "string" },
            entity_a: { type: "string" },
            entity_b: { type: "string" },
            confidence: { type: "number" },
            match_method: { type: "string" },
            tool_name: { type: "string" },
            tool_output: { type: "object" },
            context: { type: "object" },
          },
          required: ["review_type"],
        },
      },
      {
        name: "ingest_evidence",
        description: "Platform-agnostic evidence ingestor. Detects format (XML/HTML/PDF), routes to correct parser, then triggers embedding and LanceDB write.",
        inputSchema: {
          type: "object",
          properties: {
            file_path: { type: "string", description: "Absolute path to the evidence file." },
            device_id: { type: "string", description: "Optional device ID for deduplication." },
            case_id: { type: "string", description: "Optional case ID for grouping." },
            source_platform: { type: "string", description: "Optional source platform override." },
            extraction_method: { type: "string", description: "Optional extraction method label." },
          },
          required: ["file_path"],
        },
      },
      {
        name: "run_pass1_analysis",
        description: "Runs Pass 1 analysis pipeline on pending ingested files: NER extraction, entity storage, embedding, LanceDB write.",
        inputSchema: {
          type: "object",
          properties: {
            limit: { type: "integer", description: "Max items to process (default: 10).", default: 10 },
          },
        },
      },
      {
        name: "evidence_search",
        description: "Semantic search across evidence using pgvector similarity + optional keyword filter.",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string", description: "Natural language search query." },
            limit: { type: "integer", description: "Max results (default: 20).", default: 20 },
            platform: { type: "string", description: "Optional platform filter (sms, imessage, facebook)." },
            case_id: { type: "string", description: "Optional case ID filter." },
          },
          required: ["query"],
        },
      },
      // ----- SBV (SMS Backup Viewer) Tools -----
      {
        name: "sbv_ingest",
        description: "Pulls all conversations, messages, and calls from the SBV sidecar and ingests them through the full evidence pipeline (SHA-256 hash → DuckDB dedup → UUIDv7 → PostgreSQL evidence write → write tracking).",
        inputSchema: {
          type: "object",
          properties: {
            device_id: { type: "string", description: "Optional device ID for deduplication." },
            case_id: { type: "string", description: "Optional case ID for grouping." },
          },
        },
      },
      {
        name: "sbv_search",
        description: "Full-text search across messages stored in SBV (read-only, no evidence pipeline write). Useful for quick lookups before deciding to ingest.",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string", description: "Search query." },
            limit: { type: "integer", description: "Max results (default: 100).", default: 100 },
          },
          required: ["query"],
        },
      },
      {
        name: "sbv_health",
        description: "Check if the SBV sidecar service is reachable.",
        inputSchema: { type: "object", properties: {} },
      },
    ],
  }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const args = (request.params.arguments ?? {}) as Record<string, unknown>;

    switch (request.params.name) {
      case "ping":
        return { content: [{ type: "text", text: "Pong from dial-ts-core!" }] };

      case "parse_sms_xml": {
        const filePath = String(args.file_path);
        const parser = new SmsXmlParser();
        const messages = await parser.loadData(filePath);
        return { content: [{ type: "text", text: JSON.stringify(messages, null, 2) }] };
      }

      case "parse_facebook_export": {
        const filePath = String(args.file_path);
        const ownName = args.own_name ? String(args.own_name) : undefined;
        const parser = new FacebookExportParser({ ownName });
        const messages = await parser.parse(filePath);
        return { content: [{ type: "text", text: JSON.stringify(messages, null, 2) }] };
      }

      case "parse_imessage_pdf": {
        const filePath = String(args.file_path);
        const parser = new ImessagePdfParser();
        const messages = await parser.parse(filePath);
        return { content: [{ type: "text", text: JSON.stringify(messages, null, 2) }] };
      }

      case "vault_log_ingestion": {
        const { source_type, source_name, raw_content, binary_path } = args as any;
        const result = await getVault().logIngestion(source_type, source_name, raw_content ?? null, binary_path ?? null, {});
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
      }

      case "vault_get_pending_pass1": {
        const results = await getVault().getPendingPass1(50);
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
      }

      case "vault_update_pass1_status": {
        const { ingestion_id, status } = args as any;
        await getVault().updatePass1Status(ingestion_id, status);
        return { content: [{ type: "text", text: "Pass 1 status updated." }] };
      }

      case "vault_update_write_tracking": {
        const { ingestion_id, tier, written } = args as any;
        await getVault().updateWriteTracking(ingestion_id, tier, written);
        return { content: [{ type: "text", text: `Write tracking for ${tier} updated.` }] };
      }

      case "postgres_write_record": {
        const { table_name, data } = args as any;
        const result = await getPg().writeRecord(table_name, data);
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
      }

      case "postgres_raw_query": {
        const { sql, params } = args as any;
        const result = await getPg().query(sql, params ?? []);
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
      }

      case "admin_list_llm_providers": {
        const results = await getAdmin().listLlmProviders();
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
      }

      case "admin_upsert_llm_provider": {
        const result = await getAdmin().upsertLlmProvider(args as any);
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
      }

      case "admin_list_system_prompts": {
        const results = await getAdmin().listSystemPrompts();
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
      }

      case "admin_upsert_system_prompt": {
        const result = await getAdmin().upsertSystemPrompt(args as any);
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
      }

      case "review_list_pending": {
        const results = await getReview().listPending(Number(args.limit ?? 50));
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
      }

      case "review_approve": {
        const { id, reviewed_by, notes } = args as any;
        const result = await getReview().approve(id, reviewed_by, notes);
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
      }

      case "review_reject": {
        const { id, reviewed_by, notes } = args as any;
        const result = await getReview().reject(id, reviewed_by, notes);
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
      }

      case "review_submit": {
        const result = await getReview().submitForReview(args as any);
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
      }

      case "ingest_evidence": {
        const { file_path, device_id, case_id, source_platform, extraction_method } = args as any;
        const result = await getIngestor().ingest(file_path, {
          deviceId: device_id,
          caseId: case_id,
          sourcePlatform: source_platform,
          extractionMethod: extraction_method,
        });
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
      }

      case "run_pass1_analysis": {
        const limit = Number(args.limit ?? 10);
        const result = await getPass1().run(limit);
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
      }

      case "evidence_search": {
        const { query, limit, platform, case_id } = args as any;
        const maxResults = Number(limit ?? 20);

        // ---------------------------------------------------------------
        // Attempt semantic vector search via py-mcp-server
        // Falls back to keyword search if embedding service is unavailable
        // ---------------------------------------------------------------
        let vectorResults: any[] | null = null;
        try {
          // Step 1: Embed the query
          const embedResp = await fetch(
            (process.env.PY_MCP_URL ?? 'http://py-mcp-server:8082') + '/mcp',
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'tools/call',
                params: {
                  name: 'semantica_generate_embeddings',
                  arguments: { text: query },
                },
                id: 1,
              }),
              signal: AbortSignal.timeout(15000),
            },
          );

          if (embedResp.ok) {
            const embedData = (await embedResp.json()) as any;
            const embedContent = embedData?.result?.content?.[0]?.text;
            if (embedContent) {
              const { embedding } = JSON.parse(embedContent);
              if (embedding && embedding.length > 0) {
                // Step 2: Search LanceDB with the embedded query
                const searchResp = await fetch(
                  (process.env.PY_MCP_URL ?? 'http://py-mcp-server:8082') + '/mcp',
                  {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      jsonrpc: '2.0',
                      method: 'tools/call',
                      params: {
                        name: 'lancedb_vector_search',
                        arguments: {
                          collection: 'evidence_chunks',
                          query_text: query,
                          top_k: maxResults,
                        },
                      },
                      id: 2,
                    }),
                    signal: AbortSignal.timeout(15000),
                  },
                );

                if (searchResp.ok) {
                  const searchData = (await searchResp.json()) as any;
                  const searchContent = searchData?.result?.content?.[0]?.text;
                  if (searchContent) {
                    const parsed = JSON.parse(searchContent);
                    if (Array.isArray(parsed) && parsed.length > 0) {
                      vectorResults = parsed;
                    }
                  }
                }

                // Step 3: Also search PostgreSQL pgvector on evidence.messages
                if (!vectorResults || vectorResults.length === 0) {
                  const embeddingStr = `[${embedding.join(',')}]`;
                  try {
                    const pgVectorSql = platform
                      ? `SELECT id, conversation_id, sender, recipient, body, timestamp, platform, direction,
                                1 - (embedding <=> $1::vector) AS similarity
                         FROM evidence.messages
                         WHERE embedding IS NOT NULL AND platform = $2
                         ORDER BY embedding <=> $1::vector
                         LIMIT $3`
                      : `SELECT id, conversation_id, sender, recipient, body, timestamp, platform, direction,
                                1 - (embedding <=> $1::vector) AS similarity
                         FROM evidence.messages
                         WHERE embedding IS NOT NULL
                         ORDER BY embedding <=> $1::vector
                         LIMIT $2`;
                    const pgParams = platform
                      ? [embeddingStr, platform, maxResults]
                      : [embeddingStr, maxResults];
                    const pgResults = await getPg().query(pgVectorSql, pgParams);
                    if (Array.isArray(pgResults) && pgResults.length > 0) {
                      vectorResults = pgResults as any[];
                    }
                  } catch (_pgVecErr) {
                    // pgvector search failure — fall through to keyword
                  }
                }
              }
            }
          }
        } catch (_err) {
          // Embedding service unavailable — fall through to keyword search
        }

        // If vector search returned results, return them
        if (vectorResults && vectorResults.length > 0) {
          return {
            content: [{
              type: "text",
              text: JSON.stringify({
                search_type: 'semantic',
                results: vectorResults,
                count: vectorResults.length,
              }, null, 2),
            }],
          };
        }

        // ---------------------------------------------------------------
        // Fallback: keyword search
        // ---------------------------------------------------------------
        const sql = platform
          ? `SELECT id, conversation_id, sender, recipient, body, timestamp, platform, direction
             FROM evidence.messages
             WHERE body ILIKE $1 AND platform = $2
             ORDER BY timestamp DESC LIMIT $3`
          : `SELECT id, conversation_id, sender, recipient, body, timestamp, platform, direction
             FROM evidence.messages
             WHERE body ILIKE $1
             ORDER BY timestamp DESC LIMIT $2`;
        const params = platform
          ? [`%${query}%`, platform, maxResults]
          : [`%${query}%`, maxResults];
        try {
          const results = await getPg().query(sql, params);
          return {
            content: [{
              type: "text",
              text: JSON.stringify({
                search_type: 'keyword',
                results,
                count: Array.isArray(results) ? results.length : 0,
                note: 'Vector search unavailable — using keyword fallback',
              }, null, 2),
            }],
          };
        } catch (err: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: err.message }) }] };
        }
      }

      // ---- SBV (SMS Backup Viewer) Tools ----

      case "sbv_ingest": {
        const { device_id, case_id } = args as any;
        const result = await getSbvIngestor().ingest({
          deviceId: device_id,
          caseId: case_id,
        });
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
      }

      case "sbv_search": {
        const { query, limit } = args as any;
        const results = await getSbvClient().search(String(query), Number(limit ?? 100));
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
      }

      case "sbv_health": {
        const reachable = await getSbvClient().healthCheck();
        return {
          content: [{
            type: "text",
            text: JSON.stringify({
              status: reachable ? "ok" : "unreachable",
              sbv_url: process.env.SBV_URL ?? "http://sbv:8081",
              web_ui: "http://localhost:8084 (direct) or http://localhost/sbv/ (via Caddy)",
            }, null, 2),
          }],
        };
      }

      default:
        throw new Error(`Unknown tool: ${request.params.name}`);
    }
  });

  server.onerror = (error) => console.error("[MCP Error]", error);

  return server;
}

// ---------------------------------------------------------------------------
// HTTP Server — one MCP server instance per request (stateless tools)
// ---------------------------------------------------------------------------
const app = express();
app.use(express.json());

// Health check
app.get("/health", (_req, res) => {
  res.json({ status: "ok", server: "dial-ts-core", port: PORT });
});

// MCP endpoint — DIAL Core routes here via StreamableHTTP
app.all("/mcp", async (req, res) => {
  const mcpServer = createMcpServer();
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined, // Stateless — no session needed
  });
  await mcpServer.connect(transport);
  await transport.handleRequest(req, res, req.body);
  res.on("finish", () => mcpServer.close());
});

app.listen(PORT, () => {
  console.log(`[dial-ts-core] MCP HTTP server listening on port ${PORT}`);
});

// Graceful shutdown
process.on("SIGINT", () => {
  console.log("[dial-ts-core] Shutting down...");
  process.exit(0);
});
