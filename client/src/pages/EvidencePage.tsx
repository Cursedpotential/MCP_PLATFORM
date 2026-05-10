import { FileSearch, Upload } from "lucide-react";

/**
 * Evidence browser page — placeholder for future evidence search/browse UI.
 *
 * Will eventually connect to:
 * - postgres_raw_query (via MCP tools) for evidence.messages, evidence.documents
 * - evidence_search (keyword/semantic search)
 * - Directus REST API for structured data browsing
 */
export function EvidencePage() {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Evidence</h1>
        <p className="text-muted-foreground mt-1">
          Search, browse, and review ingested evidence
        </p>
      </div>

      {/* Placeholder */}
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed bg-muted/30 p-16 text-center">
        <FileSearch className="h-12 w-12 text-muted-foreground mb-4" />
        <h2 className="text-lg font-semibold">Evidence Browser</h2>
        <p className="text-sm text-muted-foreground mt-2 max-w-md">
          This page will provide a searchable interface for messages, documents,
          and analysis results stored in the evidence schema. Currently, evidence
          can be queried via the DIAL Chat interface using the{" "}
          <code className="text-xs bg-muted px-1.5 py-0.5 rounded">
            evidence_search
          </code>{" "}
          MCP tool.
        </p>
        <div className="flex gap-3 mt-6">
          <a
            href="http://localhost:3000"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Open DIAL Chat
          </a>
          <a
            href="/sbv"
            className="inline-flex items-center gap-2 rounded-lg border bg-card px-4 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            <Upload className="h-4 w-4" />
            Import via SBV
          </a>
        </div>
      </div>
    </div>
  );
}
