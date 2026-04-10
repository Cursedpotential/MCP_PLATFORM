import postgres from "postgres";

/**
 * Review Queue Tools
 * Human-in-the-loop review system for AI-generated results.
 * Ported from legacy entity_match_candidates MySQL table.
 *
 * Flow:
 *   1. AI tool generates a result (e.g., entity merge, classification)
 *   2. If confidence < threshold, tool calls review_submit_for_review
 *   3. Human reviews via review_list_pending
 *   4. Human approves (→ committed) or rejects (→ archived)
 */
export class ReviewQueue {
  private client: ReturnType<typeof postgres> | null = null;

  constructor(connectionString?: string) {
    const url = connectionString || process.env.DATABASE_URL;
    if (url) {
      this.client = postgres(url, { max: 5, idle_timeout: 20, connect_timeout: 10 });
    }
  }

  private ensureClient() {
    if (!this.client) throw new Error("DATABASE_URL not configured for PostgreSQL.");
    return this.client;
  }

  /**
   * Get all items pending human review
   */
  async listPending(limit: number = 50) {
    const sql = this.ensureClient();
    return await sql`
      SELECT id, review_type, entity_a, entity_b, confidence, match_method,
             tool_name, tool_output, context, status, created_at
      FROM app.review_queue
      WHERE status = 'PENDING'
      ORDER BY created_at ASC
      LIMIT ${limit}
    `;
  }

  /**
   * Approve a review item — marks it for commit
   */
  async approve(id: string, reviewedBy: string, notes?: string) {
    const sql = this.ensureClient();
    const result = await sql`
      UPDATE app.review_queue
      SET status = 'APPROVED',
          reviewed_by = ${reviewedBy},
          reviewed_at = NOW(),
          review_notes = ${notes || null}
      WHERE id = ${id} AND status = 'PENDING'
      RETURNING id, review_type, status
    `;
    if (result.length === 0) throw new Error(`Review item ${id} not found or already reviewed.`);
    return result[0];
  }

  /**
   * Reject a review item
   */
  async reject(id: string, reviewedBy: string, notes?: string) {
    const sql = this.ensureClient();
    const result = await sql`
      UPDATE app.review_queue
      SET status = 'REJECTED',
          reviewed_by = ${reviewedBy},
          reviewed_at = NOW(),
          review_notes = ${notes || null}
      WHERE id = ${id} AND status = 'PENDING'
      RETURNING id, review_type, status
    `;
    if (result.length === 0) throw new Error(`Review item ${id} not found or already reviewed.`);
    return result[0];
  }

  /**
   * Submit an AI result for human review before committing
   */
  async submitForReview(data: {
    review_type: string;
    entity_a?: string;
    entity_b?: string;
    confidence?: number;
    match_method?: string;
    tool_name?: string;
    tool_output?: Record<string, any>;
    context?: Record<string, any>;
  }) {
    const sql = this.ensureClient();
    return await sql`
      INSERT INTO app.review_queue
        (review_type, entity_a, entity_b, confidence, match_method, tool_name, tool_output, context)
      VALUES
        (${data.review_type}, ${data.entity_a || null}, ${data.entity_b || null},
         ${data.confidence || null}, ${data.match_method || null},
         ${data.tool_name || null}, ${JSON.stringify(data.tool_output || {})},
         ${JSON.stringify(data.context || {})})
      RETURNING id, review_type, status, created_at
    `;
  }
}
