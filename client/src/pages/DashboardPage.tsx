import {
  FileSearch,
  MessageSquare,
  Smartphone,
  Activity,
  Database,
  Server,
} from "lucide-react";

interface StatusCardProps {
  title: string;
  description: string;
  icon: React.ElementType;
  status: "online" | "offline" | "pending";
  href?: string;
}

function StatusCard({ title, description, icon: Icon, status, href }: StatusCardProps) {
  const Wrapper = href ? "a" : "div";
  const wrapperProps = href ? { href, className: "block" } : { className: "block" };

  return (
    <Wrapper {...wrapperProps}>
      <div className="rounded-xl border bg-card p-6 text-card-foreground shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between mb-4">
          <Icon className="h-5 w-5 text-muted-foreground" />
          <span
            className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium ${
              status === "online"
                ? "bg-green-500/10 text-green-600 dark:text-green-400"
                : status === "pending"
                ? "bg-yellow-500/10 text-yellow-600 dark:text-yellow-400"
                : "bg-red-500/10 text-red-600 dark:text-red-400"
            }`}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                status === "online"
                  ? "bg-green-500"
                  : status === "pending"
                  ? "bg-yellow-500"
                  : "bg-red-500"
              }`}
            />
            {status}
          </span>
        </div>
        <h3 className="font-semibold text-sm">{title}</h3>
        <p className="text-xs text-muted-foreground mt-1">{description}</p>
      </div>
    </Wrapper>
  );
}

export function DashboardPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          MCP Evidence Platform — forensic evidence processing & review
        </p>
      </div>

      {/* Service Status Grid */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Services</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <StatusCard
            title="TS MCP Server"
            description="Parsers, DuckDB vault, PostgreSQL writes"
            icon={Server}
            status="online"
          />
          <StatusCard
            title="Py MCP Server"
            description="Semantica NLP, LanceDB vectors, Neo4j graph"
            icon={Server}
            status="online"
          />
          <StatusCard
            title="SBV — SMS Viewer"
            description="SMS Backup & Restore XML viewer"
            icon={Smartphone}
            status="online"
          />
          <StatusCard
            title="PostgreSQL"
            description="Evidence & app data (pgvector enabled)"
            icon={Database}
            status="online"
          />
          <StatusCard
            title="DuckDB Vault"
            description="SHA-256 fingerprinting, ingestion log, write tracking"
            icon={Database}
            status="online"
          />
          <StatusCard
            title="DIAL Core"
            description="AI gateway — model routing & MCP dispatch"
            icon={Activity}
            status="online"
          />
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <a
            href="/evidence"
            className="flex items-center gap-4 rounded-xl border bg-card p-5 text-card-foreground shadow-sm hover:shadow-md transition-shadow"
          >
            <FileSearch className="h-8 w-8 text-primary" />
            <div>
              <h3 className="font-semibold text-sm">Browse Evidence</h3>
              <p className="text-xs text-muted-foreground">
                Search messages, documents, and analysis results
              </p>
            </div>
          </a>
          <a
            href="/conversations"
            className="flex items-center gap-4 rounded-xl border bg-card p-5 text-card-foreground shadow-sm hover:shadow-md transition-shadow"
          >
            <MessageSquare className="h-8 w-8 text-primary" />
            <div>
              <h3 className="font-semibold text-sm">Conversations</h3>
              <p className="text-xs text-muted-foreground">
                Timeline view of parsed message conversations
              </p>
            </div>
          </a>
          <a
            href="/sbv"
            className="flex items-center gap-4 rounded-xl border bg-card p-5 text-card-foreground shadow-sm hover:shadow-md transition-shadow"
          >
            <Smartphone className="h-8 w-8 text-primary" />
            <div>
              <h3 className="font-semibold text-sm">SMS Viewer (SBV)</h3>
              <p className="text-xs text-muted-foreground">
                Browse imported SMS/MMS/call backups
              </p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
}
