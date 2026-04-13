import { DuckDbVault } from './DuckDbVault.js';
import { PostgresWriter } from './PostgresWriter.js';
import { MessageChunker, MessageChunk } from './MessageChunker.js';
import { createHash } from 'crypto';

const PY_MCP_URL = process.env.PY_MCP_URL ?? 'http://py-mcp-server:8082';
const MAX_MESSAGES_PER_INGESTION = 100;

/** Batch size for embedding calls — avoid overloading py-mcp-server */
const EMBEDDING_BATCH_SIZE = 20;

export interface Pass1RunResult {
  processed: number;
  succeeded: number;
  failed: number;
  results: Array<{
    ingestion_id: string;
    status: 'completed' | 'failed';
    detail?: string;
    stats?: {
      messages: number;
      chunks: number;
      embeddings: number;
      entities: number;
      lancedb_rows: number;
    };
  }>;
}

interface EmbeddingResponse {
  embedding: number[];
  dimensions: number;
}

export class Pass1Runner {
  private readonly chunker: MessageChunker;

  constructor(
    private readonly vault: DuckDbVault,
    private readonly pg: PostgresWriter,
  ) {
    this.chunker = new MessageChunker({ chunkSize: 512, overlap: 64 });
  }

  async run(limit = 10): Promise<Pass1RunResult> {
    const pending = await this.vault.getPendingPass1(limit);
    const result: Pass1RunResult = {
      processed: pending.length,
      succeeded: 0,
      failed: 0,
      results: [],
    };

    for (const item of pending as Array<{ id: string; source_name?: string }>) {
      try {
        await this.vault.updatePass1Status(item.id, 'processing');
        const stats = await this.runPass1ForItem(item.id, item.source_name ?? item.id);
        await this.vault.updatePass1Status(item.id, 'completed');
        result.succeeded++;
        result.results.push({ ingestion_id: item.id, status: 'completed', stats });
      } catch (err: any) {
        await this.vault.updatePass1Status(item.id, 'failed').catch(() => {});
        result.failed++;
        result.results.push({ ingestion_id: item.id, status: 'failed', detail: err.message });
      }
    }

    return result;
  }

  private async runPass1ForItem(
    ingestionId: string,
    sourceName: string,
  ): Promise<{ messages: number; chunks: number; embeddings: number; entities: number; lancedb_rows: number }> {
    const stats = { messages: 0, chunks: 0, embeddings: 0, entities: 0, lancedb_rows: 0 };

    // -----------------------------------------------------------------------
    // 1. Fetch messages for this ingestion from PostgreSQL
    // -----------------------------------------------------------------------
    const messages = await this.pg.query(
      `SELECT id, body, sender, recipient, platform, timestamp, conversation_id
       FROM evidence.messages
       WHERE (provenance->>'source_ingestion_id') = $1
       LIMIT ${MAX_MESSAGES_PER_INGESTION}`,
      [ingestionId],
    );

    if (!Array.isArray(messages) || messages.length === 0) {
      return stats;
    }

    stats.messages = messages.length;

    // -----------------------------------------------------------------------
    // 2. Chunk all messages
    // -----------------------------------------------------------------------
    const allChunks = this.chunker.chunkBatch(
      (messages as unknown as Array<{
        id: string;
        body: string;
        sender: string;
        recipient: string;
        platform: string;
        timestamp: string;
        conversation_id: string;
      }>).map((msg) => ({
        id: msg.id,
        body: msg.body,
        ingestion_id: ingestionId,
        sender: msg.sender,
        recipient: msg.recipient,
        platform: msg.platform,
        timestamp: msg.timestamp,
        conversation_id: msg.conversation_id,
      })),
    );

    stats.chunks = allChunks.length;

    // Write chunks to PostgreSQL
    for (const chunk of allChunks) {
      try {
        await this.pg.writeRecord('evidence.message_chunks', {
          id: chunk.id,
          message_id: chunk.message_id,
          ingestion_id: chunk.ingestion_id,
          chunk_text: chunk.text,
          chunk_hash: chunk.chunk_hash,
          chunk_index: chunk.chunk_index,
          chunk_total: chunk.chunk_total,
          start_offset: chunk.start_offset,
          end_offset: chunk.end_offset,
          embedding_status: 'pending',
          metadata: chunk.metadata,
        });
      } catch (_err) {
        // Chunk write failure is non-fatal — may be a duplicate
      }
    }

    // -----------------------------------------------------------------------
    // 3. Generate embeddings for each chunk via py-mcp-server
    // -----------------------------------------------------------------------
    const lanceDbRecords: Array<Record<string, unknown>> = [];

    for (let i = 0; i < allChunks.length; i += EMBEDDING_BATCH_SIZE) {
      const batch = allChunks.slice(i, i + EMBEDDING_BATCH_SIZE);

      for (const chunk of batch) {
        try {
          const embedding = await this.callSemanticaEmbed(chunk.text);
          if (embedding) {
            stats.embeddings++;

            // Update chunk embedding in PostgreSQL
            await this.pg.updateEmbedding('evidence.message_chunks', chunk.id, embedding, 'embedding_status');

            // If this is the first chunk for the message (or only chunk),
            // also write the embedding to the parent message row
            if (chunk.chunk_index === 0) {
              try {
                await this.pg.updateEmbedding('evidence.messages', chunk.message_id, embedding);
              } catch (_pgErr) {
                // Non-fatal — parent update can fail if another chunk already wrote
              }
            }

            // Collect for LanceDB batch upsert
            lanceDbRecords.push({
              id: chunk.id,
              message_id: chunk.message_id,
              ingestion_id: chunk.ingestion_id,
              text: chunk.text,
              chunk_hash: chunk.chunk_hash,
              chunk_index: chunk.chunk_index,
              sender: chunk.metadata.sender ?? '',
              recipient: chunk.metadata.recipient ?? '',
              platform: chunk.metadata.platform ?? '',
              timestamp: chunk.metadata.timestamp ?? '',
              conversation_id: chunk.metadata.conversation_id ?? '',
              vector: embedding,
            });
          }
        } catch (_embErr) {
          // Embedding failure for individual chunk is non-fatal
        }
      }
    }

    // -----------------------------------------------------------------------
    // 4. Batch upsert embeddings to LanceDB
    // -----------------------------------------------------------------------
    if (lanceDbRecords.length > 0) {
      try {
        const upsertResult = await this.callLanceDbUpsert(
          'evidence_chunks',
          lanceDbRecords,
        );
        if (upsertResult) {
          stats.lancedb_rows = lanceDbRecords.length;
          await this.vault.updateWriteTracking(ingestionId, 'lancedb', true);
        }
      } catch (_lanceErr) {
        // LanceDB upsert failure is non-fatal
      }
    }

    // -----------------------------------------------------------------------
    // 5. NER extraction + graph building for each message via Semantica
    // -----------------------------------------------------------------------
    for (const msg of messages as unknown as Array<{ id: string; body: string; timestamp: string; platform: string }>) {
      if (!msg.body) continue;

      // NER extraction
      let entities: unknown[] = [];
      try {
        const nerResult = await this.callSemanticaTool('semantica_extract_entities', { text: msg.body });
        if (nerResult) {
          entities = JSON.parse(nerResult);
        }
      } catch (_err) {
        // NER failure is non-fatal
      }

      // Store NER results in forensic_results
      if (entities.length > 0) {
        stats.entities += entities.length;
        try {
          const sourceHash = createHash('sha256').update(`ner:${ingestionId}:${msg.id}`).digest('hex');
          await this.pg.writeRecord('app.forensic_results', {
            source_hash: sourceHash,
            source_type: 'ner_extraction',
            source_id: ingestionId,
            result_data: { message_id: msg.id, entities },
            created_at: new Date().toISOString(),
          });
        } catch (_pgErr) {
          // Store failure non-fatal
        }

        // Graph building — extract relations from entities
        try {
          const relationsResult = await this.callSemanticaTool('semantica_build_graph', {
            text: msg.body,
            entities_json: JSON.stringify(entities),
            metadata_json: JSON.stringify({
              message_id: msg.id,
              ingestion_id: ingestionId,
              platform: msg.platform,
            }),
          });

          if (relationsResult) {
            const relations = JSON.parse(relationsResult);

            // Extract temporal facts if we have a timestamp
            if (msg.timestamp && relations.length > 0) {
              try {
                await this.callSemanticaTool('semantica_extract_temporal_facts', {
                  entities_json: JSON.stringify(entities),
                  relations_json: JSON.stringify(relations),
                  timestamp: msg.timestamp,
                });
                // Temporal facts are stored by Semantica internally — mark Neo4j tracking
                await this.vault.updateWriteTracking(ingestionId, 'neo4j_temporal', true).catch(() => {});
              } catch (_tempErr) {
                // Temporal fact extraction is non-fatal
              }
            }

            // Store graph results
            if (relations.length > 0) {
              try {
                const graphHash = createHash('sha256').update(`graph:${ingestionId}:${msg.id}`).digest('hex');
                await this.pg.writeRecord('app.forensic_results', {
                  source_hash: graphHash,
                  source_type: 'graph_relations',
                  source_id: ingestionId,
                  result_data: { message_id: msg.id, relations },
                  created_at: new Date().toISOString(),
                });
              } catch (_pgErr) {
                // Non-fatal
              }
            }
          }
        } catch (_graphErr) {
          // Graph building failure is non-fatal
        }
      }
    }

    return stats;
  }

  // =========================================================================
  // py-mcp-server RPC helpers
  // =========================================================================

  /**
   * Call semantica_generate_embeddings on py-mcp-server and return the vector.
   */
  private async callSemanticaEmbed(text: string): Promise<number[] | null> {
    try {
      const resp = await fetch(`${PY_MCP_URL}/mcp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'tools/call',
          params: {
            name: 'semantica_generate_embeddings',
            arguments: { text },
          },
          id: 1,
        }),
        signal: AbortSignal.timeout(30000),
      });

      if (!resp.ok) return null;

      const data = (await resp.json()) as any;
      const content = data?.result?.content?.[0]?.text;
      if (!content) return null;

      const parsed: EmbeddingResponse = JSON.parse(content);
      return parsed.embedding;
    } catch (_err) {
      return null;
    }
  }

  /**
   * Call any Semantica tool on py-mcp-server and return the raw text result.
   */
  private async callSemanticaTool(
    toolName: string,
    args: Record<string, unknown>,
  ): Promise<string | null> {
    try {
      const resp = await fetch(`${PY_MCP_URL}/mcp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'tools/call',
          params: { name: toolName, arguments: args },
          id: 1,
        }),
        signal: AbortSignal.timeout(30000),
      });

      if (!resp.ok) return null;

      const data = (await resp.json()) as any;
      return data?.result?.content?.[0]?.text ?? null;
    } catch (_err) {
      return null;
    }
  }

  /**
   * Upsert embedding records to LanceDB via py-mcp-server.
   */
  private async callLanceDbUpsert(
    collection: string,
    records: Array<Record<string, unknown>>,
  ): Promise<boolean> {
    try {
      const resp = await fetch(`${PY_MCP_URL}/mcp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'tools/call',
          params: {
            name: 'lancedb_upsert',
            arguments: {
              collection,
              records_json: JSON.stringify(records),
            },
          },
          id: 1,
        }),
        signal: AbortSignal.timeout(60000),
      });

      if (!resp.ok) return false;

      const data = (await resp.json()) as any;
      const content = data?.result?.content?.[0]?.text;
      if (!content) return false;

      const result = JSON.parse(content);
      return result.success === true;
    } catch (_err) {
      return false;
    }
  }
}
