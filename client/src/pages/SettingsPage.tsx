import { Settings as SettingsIcon, ExternalLink } from "lucide-react";

/**
 * Settings page — links to platform services and configuration.
 */
export function SettingsPage() {
  const services = [
    {
      name: "DIAL Chat",
      url: "http://localhost:3000",
      description: "Admin/dev AI chat interface — access MCP tools via natural language",
    },
    {
      name: "DIAL Core API",
      url: "http://localhost:8080",
      description: "AI gateway API — model routing, tool dispatch, config",
    },
    {
      name: "SBV (SMS Backup Viewer)",
      url: "http://localhost:8084",
      description: "Standalone SBV web UI (also embedded in the SMS Viewer page)",
    },
    {
      name: "Keycloak",
      url: "http://localhost:8180",
      description: "Identity & access management — OIDC provider",
    },
    {
      name: "Directus",
      url: "http://localhost:8055",
      description: "Data/admin surface (opt-in: requires --profile data)",
    },
    {
      name: "InfluxDB",
      url: "http://localhost:8086",
      description: "Time-series analytics database",
    },
    {
      name: "Ollama",
      url: "http://localhost:11434",
      description: "Local LLM inference server",
    },
  ];

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">
          Platform configuration and service links
        </p>
      </div>

      {/* Service Links */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Platform Services</h2>
        <div className="space-y-2">
          {services.map((service) => (
            <a
              key={service.name}
              href={service.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between rounded-lg border bg-card p-4 hover:bg-accent/50 transition-colors group"
            >
              <div>
                <h3 className="text-sm font-medium">{service.name}</h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {service.description}
                </p>
              </div>
              <div className="flex items-center gap-2 text-muted-foreground group-hover:text-foreground transition-colors">
                <code className="text-xs bg-muted px-2 py-1 rounded">
                  {service.url.replace("http://", "")}
                </code>
                <ExternalLink className="h-3.5 w-3.5" />
              </div>
            </a>
          ))}
        </div>
      </div>

      {/* Platform Info */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Platform Info</h2>
        <div className="rounded-lg border bg-card p-4 space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Architecture</span>
            <span>AI DIAL Gateway + 3 MCP Servers (TS, Py, JS)</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Storage Tiers</span>
            <span>DuckDB → PostgreSQL → LanceDB → Neo4j</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Auth</span>
            <span>Keycloak OIDC</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Phase</span>
            <span>A — Foundation & Storage Tools</span>
          </div>
        </div>
      </div>
    </div>
  );
}
