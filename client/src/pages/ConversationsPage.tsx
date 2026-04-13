import { MessageSquare } from "lucide-react";

/**
 * Conversations page — placeholder for future conversation timeline view.
 *
 * Will connect to evidence.conversations and evidence.messages in PostgreSQL
 * to display a threaded timeline of parsed conversations by participant.
 */
export function ConversationsPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Conversations</h1>
        <p className="text-muted-foreground mt-1">
          Timeline view of parsed message conversations
        </p>
      </div>

      {/* Placeholder */}
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed bg-muted/30 p-16 text-center">
        <MessageSquare className="h-12 w-12 text-muted-foreground mb-4" />
        <h2 className="text-lg font-semibold">Conversation Timeline</h2>
        <p className="text-sm text-muted-foreground mt-2 max-w-md">
          This page will display a threaded view of conversations parsed from
          SMS, iMessage, Facebook, and other messaging platforms. Conversations
          are grouped by participants and sorted by timestamp.
        </p>
        <p className="text-sm text-muted-foreground mt-4 max-w-md">
          For now, use the{" "}
          <a
            href="/sbv"
            className="text-primary underline hover:text-primary/80"
          >
            SMS Viewer
          </a>{" "}
          to browse imported SMS/MMS conversations, or use the{" "}
          <a
            href="http://localhost:3000"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary underline hover:text-primary/80"
          >
            DIAL Chat
          </a>{" "}
          to query conversations via MCP tools.
        </p>
      </div>
    </div>
  );
}
