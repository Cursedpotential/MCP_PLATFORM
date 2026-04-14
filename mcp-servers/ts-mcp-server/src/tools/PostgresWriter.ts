import postgres from "postgres";
import { z } from "zod";

// =============================================================================
// Table Allowlist — Zod enum of all MCP-writable tables
// =============================================================================
// Tables NOT listed here are blocked. Attempts to write to unlisted tables
// are logged with [SECURITY] prefix and rejected.

const WRITABLE_TABLES = [
  // app schema — admin/config tables
  "app.llm_providers",
  "app.system_prompts",
  "app.workflow_templates",
  "app.behavioral_patterns",
  "app.user_settings",
  "app.review_queue",
  "app.forensic_results",
  // evidence schema — forensic data
  "evidence.messages",
  "evidence.conversations",
  "evidence.documents",
  "evidence.message_analysis",
  "evidence.analysis_runs",
  "evidence.behavioral_findings",
  "evidence.tool_execution_log",
  "evidence.message_chunks",
] as const;

const TableNameSchema = z.enum(WRITABLE_TABLES);

// =============================================================================
// Evidence Hash Requirements — tables that MUST include a hash field
// =============================================================================
// Chain-of-custody: every piece of evidence must carry a SHA-256 hash
// proving what content it represents. Missing hash = rejected write.

const EVIDENCE_HASH_REQUIRED: Record<string, string> = {
  "evidence.messages": "content_hash",
  "evidence.documents": "file_hash",
  "evidence.message_analysis": "source_hash",
  "evidence.behavioral_findings": "source_hash",
  "evidence.tool_execution_log": "input_hash",
  "evidence.message_chunks": "chunk_hash",
  "app.forensic_results": "source_hash",
};

const SHA256_REGEX = /^[a-f0-9]{64}$/;

/**
 * PostgresWriter Object
 * Exposes core PostgreSQL schema writing and querying as MCP Tools.
 *
 * Security:
 *   - Table allowlist via Zod enum — rejects writes to unlisted tables
 *   - Evidence tables require chain-of-custody hash fields
 *   - Raw queries restricted to SELECT only
 *   - All violations logged with [SECURITY] or [CHAIN-OF-CUSTODY] prefix
 */
export class PostgresWriter {
  private client: ReturnType<typeof postgres> | null = null;

  constructor(private connectionString?: string) {
    const url = this.connectionString || process.env.DATABASE_URL;
    if (url) {
      this.client = postgres(url, {
        max: 10,
        idle_timeout: 20,
        connect_timeout: 10,
      });
    }
  }

  /**
   * Insert a dynamic record into a PostgreSQL table.
   * Validates table name against allowlist and enforces hash fields
   * for evidence tables.
   */
  async writeRecord(tableName: string, data: Record<string, any>) {
    if (!this.client) {
      throw new Error("DATABASE_URL not configured for PostgreSQL.");
    }

    // --- Table allowlist validation ---
    const tableResult = TableNameSchema.safeParse(tableName);
    if (!tableResult.success) {
      const msg = `[SECURITY] Blocked write to unauthorized table: ${tableName}`;
      console.error(msg);
      throw new Error(msg);
    }

    // --- Chain-of-custody hash validation ---
    const requiredHashField = EVIDENCE_HASH_REQUIRED[tableName];
    if (requiredHashField) {
      const hashValue = data[requiredHashField];

      if (!hashValue) {
        const msg = `[CHAIN-OF-CUSTODY] Write to ${tableName} rejected: missing required hash field '${requiredHashField}'`;
        console.error(msg);
        throw new Error(msg);
      }

      if (typeof hashValue !== "string" || !SHA256_REGEX.test(hashValue)) {
        const msg = `[CHAIN-OF-CUSTODY] Write to ${tableName} rejected: '${requiredHashField}' must be a valid SHA-256 hash (64 lowercase hex chars), got: ${String(hashValue).substring(0, 20)}...`;
        console.error(msg);
        throw new Error(msg);
      }
    }

    try {
      const result = await this.client`
        INSERT INTO ${this.client(tableName)} ${this.client(data)}
        RETURNING *
      `;
      return result;
    } catch (error: any) {
      console.error(`[PostgresWriter] Failed to write to ${tableName}:`, error);
      throw new Error(`Failed to write to ${tableName}: ${error.message}`);
    }
  }

  /**
   * Execute a read-only SELECT query against PostgreSQL.
   * Non-SELECT statements (INSERT, UPDATE, DELETE, DROP, etc.) are blocked.
   */
  async query(sql: string, params: any[] = []) {
    if (!this.client) {
      throw new Error("DATABASE_URL not configured for PostgreSQL.");
    }

    // --- SELECT-only enforcement ---
    const normalized = sql.trim().toUpperCase();
    if (!normalized.startsWith("SELECT")) {
      const msg = `[SECURITY] Blocked non-SELECT query: ${sql.substring(0, 80)}...`;
      console.error(msg);
      throw new Error(
        `[SECURITY] Only SELECT queries are allowed via postgres_raw_query. Use postgres_write_record for writes.`
      );
    }

    try {
      const result = await this.client.unsafe(sql, params);
      return result;
    } catch (error: any) {
      // Sanitize error — don't expose internal schema details
      console.error(`[PostgresWriter] Query failed:`, error);
      throw new Error(`Query failed: ${error.code || "UNKNOWN"}`);
    }
  }

  /**
   * Update a record's embedding column by ID.
   * Restricted to specific embedding update patterns for safety.
   */
  async updateEmbedding(
    tableName: string,
    id: string,
    embedding: number[],
    statusField?: string,
  ) {
    if (!this.client) {
      throw new Error("DATABASE_URL not configured for PostgreSQL.");
    }

    // Only allow embedding updates on known tables
    const EMBEDDABLE_TABLES = ["evidence.messages", "evidence.message_chunks"];
    if (!EMBEDDABLE_TABLES.includes(tableName)) {
      throw new Error(`[SECURITY] Embedding update not allowed on table: ${tableName}`);
    }

    // Whitelist of allowed status field names to prevent SQL injection
    const ALLOWED_STATUS_FIELDS = ["embedding_status"];
    if (statusField && !ALLOWED_STATUS_FIELDS.includes(statusField)) {
      throw new Error(`[SECURITY] Status field '${statusField}' is not in the allowed list`);
    }

    const embeddingStr = `[${embedding.join(",")}]`;

    try {
      if (statusField) {
        await this.client.unsafe(
          `UPDATE ${tableName} SET embedding = $1::vector, ${statusField} = 'completed', updated_at = NOW() WHERE id = $2`,
          [embeddingStr, id],
        );
      } else {
        await this.client.unsafe(
          `UPDATE ${tableName} SET embedding = $1::vector, updated_at = NOW() WHERE id = $2`,
          [embeddingStr, id],
        );
      }
    } catch (error: any) {
      console.error(`[PostgresWriter] Embedding update failed for ${tableName}:`, error);
      throw new Error(`Embedding update failed: ${error.message}`);
    }
  }
}
