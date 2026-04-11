import { DuckDBClient, getDuckDBClient, IngestionLog } from "../services/DuckDbService.js";

/**
 * DuckDbVault Object
 * Exposes core DuckDB forensic chain-of-custody logging as pure MCP Tools.
 */
export class DuckDbVault {
  private client: DuckDBClient;

  constructor() {
    this.client = getDuckDBClient({
      // Re-route path into the new dial-stack folder for safety/isolation
      path: "./data/duckdb/forensic_vault.db",
      readOnly: false
    });
  }

  async initialize(): Promise<void> {
    if (!this.client.isInitialized()) {
      await this.client.initialize();
    }
  }

  /**
   * Calculates a SHA-256 hash for the given content (chain of custody at first touch).
   */
  async hashContent(content: string | Buffer): Promise<string> {
    await this.initialize();
    return this.client.hashContent(content);
  }

  /**
   * Looks up an existing ingestion by its source hash (deduplication check).
   */
  async getIngestionByHash(hash: string): Promise<IngestionLog | null> {
    await this.initialize();
    return this.client.getIngestionByHash(hash);
  }

  /**
   * Logs a new ingestion file into the forensic vault and returns the ID
   */
  async logIngestion(
    sourceType: string,
    sourceName: string,
    rawContent: string | null = null,
    binaryPath: string | null = null,
    metadata: Record<string, unknown> = {}
  ) {
    await this.initialize();
    return await this.client.logIngestion(sourceType, sourceName, rawContent, binaryPath, metadata);
  }

  /**
   * Gets a list of files that have been parsed but not yet embedded
   */
  async getPendingPass1(limit: number = 50) {
    await this.initialize();
    return await this.client.getPendingPass1(limit);
  }

  /**
   * Updates tracking to indicate a file has been written to a specific lower tier
   */
  async updateWriteTracking(
    ingestionId: string,
    tier: "lancedb" | "neo4j_semantic" | "neo4j_temporal" | "postgresql",
    written: boolean = true
  ) {
    await this.initialize();
    return await this.client.updateWriteTracking(ingestionId, tier, written);
  }

  /**
   * Update the status of passing a file to pass 1 (embeddings/vectors)
   */
  async updatePass1Status(ingestionId: string, status: "pending" | "processing" | "completed" | "failed") {
    await this.initialize();
    return await this.client.updatePass1Status(ingestionId, status);
  }
}
