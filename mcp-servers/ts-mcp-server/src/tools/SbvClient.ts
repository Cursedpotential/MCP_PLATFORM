/**
 * SbvClient — Typed HTTP client for the SBV (SMS Backup Viewer) REST API.
 *
 * SBV is a Go-based web app (ghcr.io/lowcarbdev/sbv) that parses SMS Backup &
 * Restore XML files into a browsable SQLite-backed web UI.  This client talks
 * to its internal REST API so the MCP platform can pull parsed conversations
 * and messages back through the evidence pipeline (hash → DuckDB → PostgreSQL).
 *
 * Auth: SBV uses cookie-based sessions.  We call /api/login once, cache the
 * session cookie, and re-auth automatically on 401.
 */

// ---------------------------------------------------------------------------
// Types — mirror what the SBV REST API returns
// ---------------------------------------------------------------------------

export interface SbvConversation {
  id: number;
  address: string;
  contact_name: string;
  message_count: number;
  last_message_date: string;   // ISO-8601 or epoch-ms depending on SBV version
}

export interface SbvMessage {
  id: number;
  address: string;
  contact_name: string;
  body: string;
  date: string;                // epoch-ms as string
  type: number;                // 1=received, 2=sent, 3=draft, etc.
  read: number;
  status: number;
  // MMS fields (optional)
  ct_t?: string;
  msg_box?: number;
  parts?: SbvMmsPart[];
}

export interface SbvMmsPart {
  content_type: string;
  text?: string;
  data?: string;               // base64 for binary parts
}

export interface SbvCall {
  id: number;
  number: string;
  contact_name: string;
  date: string;
  duration: number;
  type: number;                // 1=incoming, 2=outgoing, 3=missed, etc.
}

export interface SbvSearchResult {
  messages: SbvMessage[];
  total: number;
}

export interface SbvDateRange {
  min_date: string;
  max_date: string;
}

export interface SbvClientConfig {
  baseUrl: string;
  username?: string;
  password?: string;
  /** Request timeout in milliseconds (default 15 000) */
  timeoutMs?: number;
}

// ---------------------------------------------------------------------------
// Client implementation
// ---------------------------------------------------------------------------

export class SbvClient {
  private readonly baseUrl: string;
  private readonly username: string;
  private readonly password: string;
  private readonly timeoutMs: number;
  private sessionCookie: string | null = null;

  constructor(config?: Partial<SbvClientConfig>) {
    this.baseUrl = (config?.baseUrl ?? process.env.SBV_URL ?? 'http://sbv:8081').replace(/\/+$/, '');
    this.username = config?.username ?? process.env.SBV_USERNAME ?? '';
    this.password = config?.password ?? process.env.SBV_PASSWORD ?? '';
    this.timeoutMs = config?.timeoutMs ?? 15_000;
  }

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------

  /** Health-check — returns true if SBV is reachable. */
  async healthCheck(): Promise<boolean> {
    try {
      const resp = await this.get('/api/me');
      return resp.ok || resp.status === 401; // 401 = reachable but not logged in
    } catch {
      return false;
    }
  }

  /** Get all conversations. */
  async getConversations(): Promise<SbvConversation[]> {
    return this.authenticatedJson<SbvConversation[]>('/api/conversations');
  }

  /** Get messages for a conversation by address (phone number). */
  async getMessages(address: string): Promise<SbvMessage[]> {
    return this.authenticatedJson<SbvMessage[]>(`/api/messages?address=${encodeURIComponent(address)}`);
  }

  /** Get all messages (no filter). */
  async getAllMessages(): Promise<SbvMessage[]> {
    return this.authenticatedJson<SbvMessage[]>('/api/messages');
  }

  /** Get call log entries. */
  async getCalls(): Promise<SbvCall[]> {
    return this.authenticatedJson<SbvCall[]>('/api/calls');
  }

  /** Full-text search across messages. */
  async search(query: string, limit = 100): Promise<SbvSearchResult> {
    return this.authenticatedJson<SbvSearchResult>(
      `/api/search?q=${encodeURIComponent(query)}&limit=${limit}`,
    );
  }

  /** Get the date range of imported data. */
  async getDateRange(): Promise<SbvDateRange> {
    return this.authenticatedJson<SbvDateRange>('/api/stats');
  }

  // -------------------------------------------------------------------------
  // Internal HTTP helpers
  // -------------------------------------------------------------------------

  /** Make a GET request (no auth). */
  private async get(path: string, headers: Record<string, string> = {}): Promise<Response> {
    return fetch(`${this.baseUrl}${path}`, {
      method: 'GET',
      headers,
      signal: AbortSignal.timeout(this.timeoutMs),
    });
  }

  /** Authenticate by calling /api/login, cache the session cookie. */
  private async login(): Promise<void> {
    if (!this.username) {
      // SBV may be running in single-user / no-auth mode — skip login
      return;
    }
    const resp = await fetch(`${this.baseUrl}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: this.username, password: this.password }),
      signal: AbortSignal.timeout(this.timeoutMs),
    });

    if (!resp.ok) {
      throw new Error(`SBV login failed: HTTP ${resp.status}`);
    }

    // Extract Set-Cookie header
    const setCookie = resp.headers.get('set-cookie');
    if (setCookie) {
      // Keep only the cookie name=value portion (strip path/domain/flags)
      this.sessionCookie = setCookie.split(';')[0];
    }
  }

  /**
   * Authenticated JSON GET with automatic re-auth on 401.
   * If SBV has no auth enabled (no username configured) we still make the
   * request without a cookie — SBV will serve it in single-user mode.
   */
  private async authenticatedJson<T>(path: string): Promise<T> {
    // First attempt
    let resp = await this.authedGet(path);

    // Re-auth on 401 (session expired or not yet logged in)
    if (resp.status === 401) {
      await this.login();
      resp = await this.authedGet(path);
    }

    if (!resp.ok) {
      const body = await resp.text().catch(() => '');
      throw new Error(`SBV API error: ${resp.status} ${resp.statusText} — ${body}`);
    }

    return resp.json() as Promise<T>;
  }

  private async authedGet(path: string): Promise<Response> {
    const headers: Record<string, string> = {};
    if (this.sessionCookie) {
      headers['Cookie'] = this.sessionCookie;
    }
    return this.get(path, headers);
  }
}
