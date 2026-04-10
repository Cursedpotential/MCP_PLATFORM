import postgres from "postgres";

/**
 * Admin Tools
 * MCP tools for managing LLM providers, API keys, and system prompts.
 * Reads/writes from the app.* PostgreSQL schema.
 */
export class AdminTools {
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

  // =========================================================================
  // LLM Provider Management
  // =========================================================================

  async listLlmProviders() {
    const sql = this.ensureClient();
    return await sql`
      SELECT id, provider_name, base_url, is_active, priority, usage_count, total_cost_cents, created_at
      FROM app.llm_providers
      ORDER BY priority DESC, created_at DESC
    `;
  }

  async upsertLlmProvider(data: {
    user_id?: number;
    provider_name: string;
    api_key_encrypted: string;
    base_url?: string;
    is_active?: boolean;
    priority?: number;
  }) {
    const sql = this.ensureClient();
    const userId = data.user_id || 1; // Default admin user

    // Check if provider exists by name
    const existing = await sql`
      SELECT id FROM app.llm_providers WHERE provider_name = ${data.provider_name} LIMIT 1
    `;

    if (existing.length > 0) {
      return await sql`
        UPDATE app.llm_providers
        SET api_key_encrypted = ${data.api_key_encrypted},
            base_url = ${data.base_url || null},
            is_active = ${data.is_active ?? true},
            priority = ${data.priority ?? 0},
            updated_at = NOW()
        WHERE id = ${existing[0].id}
        RETURNING id, provider_name, base_url, is_active, priority
      `;
    }

    return await sql`
      INSERT INTO app.llm_providers (user_id, provider_name, api_key_encrypted, base_url, is_active, priority)
      VALUES (${userId}, ${data.provider_name}, ${data.api_key_encrypted}, ${data.base_url || null}, ${data.is_active ?? true}, ${data.priority ?? 0})
      RETURNING id, provider_name, base_url, is_active, priority
    `;
  }

  // =========================================================================
  // System Prompt Management
  // =========================================================================

  async listSystemPrompts() {
    const sql = this.ensureClient();
    return await sql`
      SELECT id, name, description, tool_name, version, is_active, usage_count, created_at
      FROM app.system_prompts
      ORDER BY name, version DESC
    `;
  }

  async upsertSystemPrompt(data: {
    user_id?: number;
    name: string;
    description?: string;
    tool_name?: string;
    prompt_text: string;
    variables?: Record<string, any>;
  }) {
    const sql = this.ensureClient();
    const userId = data.user_id || 1;

    // Find current version
    const existing = await sql`
      SELECT id, version FROM app.system_prompts
      WHERE name = ${data.name}
      ORDER BY version DESC LIMIT 1
    `;

    const nextVersion = existing.length > 0 ? existing[0].version + 1 : 1;
    const parentId = existing.length > 0 ? existing[0].id : null;

    return await sql`
      INSERT INTO app.system_prompts (user_id, name, description, tool_name, prompt_text, variables, version, parent_id)
      VALUES (${userId}, ${data.name}, ${data.description || null}, ${data.tool_name || null},
              ${data.prompt_text}, ${JSON.stringify(data.variables || {})}, ${nextVersion}, ${parentId})
      RETURNING id, name, version, is_active
    `;
  }
}
