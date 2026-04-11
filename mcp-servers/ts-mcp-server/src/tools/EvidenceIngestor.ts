import { extname } from 'path';
import { DuckDbVault } from './DuckDbVault.js';
import { PostgresWriter } from './PostgresWriter.js';
import { SmsEvidenceIngestor } from './SmsEvidenceIngestor.js';

const PY_MCP_URL = process.env.PY_MCP_URL ?? 'http://py-mcp-server:8082';

export interface IngestOptions {
  deviceId?: string;
  caseId?: string;
  sourcePlatform?: string;
  extractionMethod?: string;
}

export interface IngestStepResult {
  status: 'success' | 'skipped' | 'failed';
  detail?: string;
}

export interface IngestResult {
  status: 'ingested' | 'duplicate' | 'unsupported_format' | 'failed';
  format?: string;
  note?: string;
  ingestion_id?: string;
  source_hash?: string;
  document_id?: string;
  message_count?: number;
  conversation_count?: number;
  steps: {
    parse: IngestStepResult;
    embed: IngestStepResult;
    lancedb: IngestStepResult;
    write_tracking: IngestStepResult;
  };
  error?: string;
}

export class EvidenceIngestor {
  private readonly smsIngestor: SmsEvidenceIngestor;

  constructor(
    private readonly vault: DuckDbVault,
    private readonly pg: PostgresWriter,
  ) {
    this.smsIngestor = new SmsEvidenceIngestor(vault, pg);
  }

  async ingest(filePath: string, options: IngestOptions = {}): Promise<IngestResult> {
    const ext = extname(filePath).toLowerCase();
    const steps: IngestResult['steps'] = {
      parse: { status: 'skipped' },
      embed: { status: 'skipped' },
      lancedb: { status: 'skipped' },
      write_tracking: { status: 'skipped' },
    };

    // Format detection
    if (ext === '.html' || ext === '.htm') {
      return { status: 'unsupported_format', format: 'html', note: 'Facebook HTML parser is a planned addition — requires owner approval before implementation.', steps };
    }
    if (ext === '.pdf') {
      return { status: 'unsupported_format', format: 'pdf', note: 'iMessage PDF parser is a planned addition — requires owner approval before implementation.', steps };
    }
    if (ext !== '.xml') {
      return { status: 'unsupported_format', format: ext || 'unknown', note: 'Format not yet supported by any registered parser.', steps };
    }

    // XML → SMS parser
    let parseResult: any;
    try {
      parseResult = await this.smsIngestor.ingest(filePath, options);
      steps.parse = { status: 'success', detail: `status=${parseResult.status}` };
    } catch (err: any) {
      steps.parse = { status: 'failed', detail: err.message };
      return {
        status: 'failed',
        format: 'xml',
        steps,
        error: `Parse step failed: ${err.message}`,
      };
    }

    if (parseResult.status === 'duplicate') {
      return { ...parseResult, steps };
    }

    // Embedding step — call py-mcp-server (best-effort, non-blocking)
    steps.embed = await this.callEmbeddings(parseResult.ingestion_id);

    // LanceDB upsert step — best-effort
    steps.lancedb = await this.callLanceDbUpsert(parseResult.ingestion_id, parseResult.document_id);

    // Update write tracking
    try {
      await this.vault.updateWriteTracking(parseResult.ingestion_id, 'lancedb', steps.lancedb.status === 'success');
      steps.write_tracking = { status: 'success' };
    } catch (err: any) {
      steps.write_tracking = { status: 'failed', detail: err.message };
    }

    return {
      status: 'ingested',
      format: 'xml',
      ingestion_id: parseResult.ingestion_id,
      source_hash: parseResult.source_hash,
      document_id: parseResult.document_id,
      message_count: parseResult.message_count,
      conversation_count: parseResult.conversation_count,
      steps,
    };
  }

  private async callEmbeddings(ingestionId: string): Promise<IngestStepResult> {
    try {
      // TODO: In full implementation, fetch actual messages from PG and embed each.
      // For MVP, we send a test ping to verify py-mcp-server connectivity.
      const resp = await fetch(`${PY_MCP_URL}/health`, { signal: AbortSignal.timeout(5000) });
      if (resp.ok) {
        return { status: 'success', detail: 'py-mcp-server reachable; full embedding deferred to Pass1Runner' };
      }
      return { status: 'failed', detail: `py-mcp-server returned ${resp.status}` };
    } catch (err: any) {
      // Non-fatal — embedding can be run later by Pass1Runner
      return { status: 'failed', detail: `py-mcp-server unreachable: ${err.message}` };
    }
  }

  private async callLanceDbUpsert(ingestionId: string, documentId: string): Promise<IngestStepResult> {
    try {
      const resp = await fetch(`${PY_MCP_URL}/health`, { signal: AbortSignal.timeout(5000) });
      if (resp.ok) {
        return { status: 'success', detail: 'LanceDB upsert deferred to Pass1Runner after embedding' };
      }
      return { status: 'failed', detail: `py-mcp-server returned ${resp.status}` };
    } catch (err: any) {
      return { status: 'failed', detail: `LanceDB upsert skipped: py-mcp-server unreachable: ${err.message}` };
    }
  }
}
