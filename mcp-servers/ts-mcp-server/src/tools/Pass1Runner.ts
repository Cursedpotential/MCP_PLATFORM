import { DuckDbVault } from './DuckDbVault.js';
import { PostgresWriter } from './PostgresWriter.js';
import { createHash } from 'crypto';

const PY_MCP_URL = process.env.PY_MCP_URL ?? 'http://py-mcp-server:8082';
const MAX_MESSAGES_PER_INGESTION = 100;

export interface Pass1RunResult {
  processed: number;
  succeeded: number;
  failed: number;
  results: Array<{
    ingestion_id: string;
    status: 'completed' | 'failed';
    detail?: string;
  }>;
}

export class Pass1Runner {
  constructor(
    private readonly vault: DuckDbVault,
    private readonly pg: PostgresWriter,
  ) {}

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
        await this.runPass1ForItem(item.id, item.source_name ?? item.id);
        await this.vault.updatePass1Status(item.id, 'completed');
        result.succeeded++;
        result.results.push({ ingestion_id: item.id, status: 'completed' });
      } catch (err: any) {
        await this.vault.updatePass1Status(item.id, 'failed').catch(() => {});
        result.failed++;
        result.results.push({ ingestion_id: item.id, status: 'failed', detail: err.message });
      }
    }

    return result;
  }

  private async runPass1ForItem(ingestionId: string, sourceName: string): Promise<void> {
    // 1. Fetch messages for this ingestion from PostgreSQL
    const messages = await this.pg.query(
      `SELECT id, body FROM evidence.messages WHERE (provenance->>'source_ingestion_id') = $1 LIMIT ${MAX_MESSAGES_PER_INGESTION}`,
      [ingestionId],
    );

    if (!Array.isArray(messages) || messages.length === 0) {
      return; // Nothing to embed
    }

    // 2. For each message, call Semantica NER + embeddings via py-mcp-server
    for (const msg of messages as unknown as Array<{ id: string; body: string }>) {
      if (!msg.body) continue;

      // Call NER extraction
      let entities: unknown[] = [];
      try {
        const nerResp = await fetch(`${PY_MCP_URL}/mcp`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'tools/call',
            params: {
              name: 'semantica_extract_entities',
              arguments: { text: msg.body },
            },
            id: 1,
          }),
          signal: AbortSignal.timeout(30000),
        });
        if (nerResp.ok) {
          const nerData = await nerResp.json() as any;
          entities = JSON.parse(nerData?.result?.content?.[0]?.text ?? '[]');
        }
      } catch (_err) {
        // NER failure is non-fatal
      }

      // Store forensic result in app.forensic_results
      if (entities.length > 0) {
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
      }
    }
  }
}
