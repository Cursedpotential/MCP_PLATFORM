import { useState } from "react";
import {
  ExternalLink,
  KeyRound,
  HardDrive,
  Server,
  Info,
  Eye,
  EyeOff,
  Copy,
  Plus,
  ShieldCheck,
  Cloud,
  Brain,
  FileText,
  Plug,
} from "lucide-react";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Tab definitions
// ---------------------------------------------------------------------------

const tabs = [
  { id: "secrets", label: "Secrets & Keys", icon: KeyRound },
  { id: "storage", label: "Storage", icon: HardDrive },
  { id: "services", label: "Services", icon: Server },
  { id: "general", label: "General", icon: Info },
] as const;

type TabId = (typeof tabs)[number]["id"];

// ---------------------------------------------------------------------------
// Settings Page — tabbed config surface
// ---------------------------------------------------------------------------

export function SettingsPage() {
  const [activeTab, setActiveTab] = useState<TabId>("secrets");

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">
          Platform configuration, secrets, storage, and service management
        </p>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 border-b">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px",
              activeTab === tab.id
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
            )}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div>
        {activeTab === "secrets" && <SecretsSection />}
        {activeTab === "storage" && <StorageSection />}
        {activeTab === "services" && <ServicesSection />}
        {activeTab === "general" && <GeneralSection />}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Secrets & API Keys
// ---------------------------------------------------------------------------

interface SecretEntry {
  key: string;
  envVar: string;
  description: string;
  placeholder: string;
  sensitive: boolean;
}

interface SecretGroup {
  title: string;
  icon: React.ElementType;
  description: string;
  secrets: SecretEntry[];
}

const secretGroups: SecretGroup[] = [
  {
    title: "Platform Access",
    icon: ShieldCheck,
    description:
      "JWT tokens and API keys for accessing the MCP Platform. Managed via Keycloak OIDC or DIAL Core static keys.",
    secrets: [
      {
        key: "DIAL Admin Key",
        envVar: "dial_admin_key",
        description: "Full admin access — all models, all tools, all MCP servers",
        placeholder: "Configured in config.json → keys",
        sensitive: true,
      },
      {
        key: "DIAL API Key",
        envVar: "dial_api_key",
        description: "Default user access — models + ingestion agent",
        placeholder: "Configured in config.json → keys",
        sensitive: true,
      },
      {
        key: "DIAL Read-Only Key",
        envVar: "dial_readonly_key",
        description: "Read-only access — Ollama local only",
        placeholder: "Configured in config.json → keys",
        sensitive: true,
      },
      {
        key: "Keycloak Admin",
        envVar: "KEYCLOAK_ADMIN",
        description: "Keycloak admin console login",
        placeholder: "admin",
        sensitive: false,
      },
      {
        key: "Keycloak Admin Password",
        envVar: "KEYCLOAK_ADMIN_PASSWORD",
        description: "Keycloak admin console password",
        placeholder: "••••••••",
        sensitive: true,
      },
    ],
  },
  {
    title: "LLM Providers",
    icon: Brain,
    description: "API keys for language model providers routed through DIAL Core.",
    secrets: [
      {
        key: "OpenRouter API Key",
        envVar: "OPENROUTER_API_KEY",
        description: "Multi-model router — routes to Claude, GPT, Gemini, etc.",
        placeholder: "sk-or-v1-...",
        sensitive: true,
      },
    ],
  },
  {
    title: "Cloud Storage",
    icon: Cloud,
    description: "Credentials for S3-compatible object storage (Cloudflare R2, AWS S3, etc.).",
    secrets: [
      {
        key: "R2 Endpoint URL",
        envVar: "R2_ENDPOINT_URL",
        description: "Cloudflare R2 or S3-compatible endpoint",
        placeholder: "https://your-account-id.r2.cloudflarestorage.com",
        sensitive: false,
      },
      {
        key: "R2 Access Key ID",
        envVar: "R2_ACCESS_KEY_ID",
        description: "S3-compatible access key",
        placeholder: "your_r2_access_key_id",
        sensitive: true,
      },
      {
        key: "R2 Secret Access Key",
        envVar: "R2_SECRET_ACCESS_KEY",
        description: "S3-compatible secret key",
        placeholder: "••••••••",
        sensitive: true,
      },
      {
        key: "R2 Bucket Name",
        envVar: "R2_BUCKET_NAME",
        description: "Target bucket for DIAL Core file storage",
        placeholder: "your_bucket_name",
        sensitive: false,
      },
    ],
  },
  {
    title: "Document Intelligence",
    icon: FileText,
    description:
      "API keys for cloud document processing engines (optional — only needed if using cloud engines).",
    secrets: [
      {
        key: "Google DocAI Credentials",
        envVar: "GOOGLE_APPLICATION_CREDENTIALS",
        description: "Path to GCP service account JSON",
        placeholder: "/path/to/service-account.json",
        sensitive: false,
      },
      {
        key: "Google DocAI Project ID",
        envVar: "GOOGLE_DOCAI_PROJECT_ID",
        description: "GCP project for Document AI",
        placeholder: "your-gcp-project-id",
        sensitive: false,
      },
      {
        key: "AWS Access Key ID",
        envVar: "AWS_ACCESS_KEY_ID",
        description: "AWS credentials for Textract / Rekognition",
        placeholder: "your_aws_access_key_id",
        sensitive: true,
      },
      {
        key: "AWS Secret Access Key",
        envVar: "AWS_SECRET_ACCESS_KEY",
        description: "AWS secret key",
        placeholder: "••••••••",
        sensitive: true,
      },
      {
        key: "LlamaCloud API Key",
        envVar: "LLAMA_CLOUD_API_KEY",
        description: "LlamaParse cloud document parser",
        placeholder: "llx-...",
        sensitive: true,
      },
      {
        key: "watsonx API Key",
        envVar: "WATSONX_API_KEY",
        description: "IBM watsonx.ai document understanding",
        placeholder: "your_watsonx_api_key",
        sensitive: true,
      },
      {
        key: "GLM-OCR API Key",
        envVar: "GLM_OCR_API_KEY",
        description: "GLM-OCR cloud endpoint (optional, local GPU preferred)",
        placeholder: "your_glm_ocr_api_key",
        sensitive: true,
      },
    ],
  },
  {
    title: "MCP & Service Auth",
    icon: Plug,
    description: "Credentials for connected services — databases, knowledge graph, sidecars.",
    secrets: [
      {
        key: "PostgreSQL Password",
        envVar: "POSTGRES_PASSWORD",
        description: "PostgreSQL password for the 'dial' user",
        placeholder: "dial_password",
        sensitive: true,
      },
      {
        key: "Neo4j URI",
        envVar: "NEO4J_URI",
        description: "Knowledge graph connection string",
        placeholder: "bolt://neo4j:7687",
        sensitive: false,
      },
      {
        key: "Neo4j Password",
        envVar: "NEO4J_PASSWORD",
        description: "Neo4j authentication password",
        placeholder: "••••••••",
        sensitive: true,
      },
      {
        key: "Directus Key",
        envVar: "DIRECTUS_KEY",
        description: "Directus encryption key (change in production!)",
        placeholder: "supersecretkey-change-me",
        sensitive: true,
      },
      {
        key: "Directus Secret",
        envVar: "DIRECTUS_SECRET",
        description: "Directus JWT secret (change in production!)",
        placeholder: "••••••••",
        sensitive: true,
      },
      {
        key: "SBV Username",
        envVar: "SBV_USERNAME",
        description: "SBV login (empty = no-auth mode)",
        placeholder: "(optional)",
        sensitive: false,
      },
      {
        key: "SBV Password",
        envVar: "SBV_PASSWORD",
        description: "SBV login password",
        placeholder: "••••••••",
        sensitive: true,
      },
    ],
  },
];

function SecretRow({ entry }: { entry: SecretEntry }) {
  const [visible, setVisible] = useState(false);

  return (
    <div className="flex items-center justify-between py-3 px-4 rounded-lg hover:bg-muted/50 transition-colors">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{entry.key}</span>
          <code className="text-[10px] bg-muted px-1.5 py-0.5 rounded text-muted-foreground">
            {entry.envVar}
          </code>
        </div>
        <p className="text-xs text-muted-foreground mt-0.5">{entry.description}</p>
      </div>
      <div className="flex items-center gap-1.5 ml-4 shrink-0">
        <span className="text-xs text-muted-foreground font-mono max-w-[160px] truncate">
          {entry.sensitive && !visible ? "••••••••" : entry.placeholder}
        </span>
        {entry.sensitive && (
          <button
            onClick={() => setVisible(!visible)}
            className="p-1 rounded hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
            title={visible ? "Hide" : "Show"}
          >
            {visible ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
          </button>
        )}
        <button
          className="p-1 rounded hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
          title="Copy env var name"
          onClick={() => navigator.clipboard?.writeText(entry.envVar)}
        >
          <Copy className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}

function SecretsSection() {
  return (
    <div className="space-y-6">
      <div className="rounded-lg border bg-amber-500/5 border-amber-500/20 p-4">
        <p className="text-sm text-amber-700 dark:text-amber-400">
          <strong>Environment-based secrets.</strong> Values are stored in your{" "}
          <code className="text-xs bg-amber-500/10 px-1.5 py-0.5 rounded">.env</code> file and
          injected into containers via Docker Compose. They are{" "}
          <strong>never stored in the browser</strong>. This page shows which keys are expected and
          lets you copy env var names. To change a value, edit{" "}
          <code className="text-xs bg-amber-500/10 px-1.5 py-0.5 rounded">.env</code> and restart
          the affected service.
        </p>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {secretGroups.reduce((n, g) => n + g.secrets.length, 0)} keys across{" "}
          {secretGroups.length} domains
        </p>
        <a
          href="http://localhost:8180"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 rounded-md border bg-card px-3 py-1.5 text-xs font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
        >
          <ShieldCheck className="h-3.5 w-3.5" />
          Open Keycloak
          <ExternalLink className="h-3 w-3" />
        </a>
      </div>

      {secretGroups.map((group) => (
        <div key={group.title} className="rounded-xl border bg-card overflow-hidden">
          <div className="flex items-center gap-3 px-4 py-3 border-b bg-muted/30">
            <group.icon className="h-4 w-4 text-muted-foreground" />
            <div>
              <h3 className="text-sm font-semibold">{group.title}</h3>
              <p className="text-xs text-muted-foreground">{group.description}</p>
            </div>
          </div>
          <div className="divide-y divide-border/50">
            {group.secrets.map((entry) => (
              <SecretRow key={entry.envVar} entry={entry} />
            ))}
          </div>
        </div>
      ))}

      <div className="rounded-lg border border-dashed bg-muted/20 p-6 text-center">
        <Plus className="h-6 w-6 mx-auto text-muted-foreground mb-2" />
        <p className="text-sm font-medium">Need to add a new key?</p>
        <p className="text-xs text-muted-foreground mt-1 max-w-md mx-auto">
          Add the environment variable to{" "}
          <code className="bg-muted px-1 py-0.5 rounded">.env.example</code>, reference it in{" "}
          <code className="bg-muted px-1 py-0.5 rounded">docker-compose.yml</code>, and restart
          the service. Future versions will support runtime key rotation via Context Forge.
        </p>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Storage Configuration
// ---------------------------------------------------------------------------

function StorageSection() {
  const storageTiers = [
    {
      name: "DuckDB Vault",
      type: "Embedded (file-based)",
      purpose: "SHA-256 fingerprinting, ingestion log, write tracking, master clock",
      path: "./data/duckdb/forensic_vault.db",
      configurable: false,
    },
    {
      name: "PostgreSQL",
      type: "Container (pgvector/pgvector:pg16)",
      purpose: "Normalized evidence, conversations, messages, app data",
      path: "pgdata volume → /var/lib/postgresql/data",
      configurable: true,
      envVars: ["POSTGRES_PASSWORD"],
    },
    {
      name: "LanceDB",
      type: "Embedded (file-based)",
      purpose: "Vector embeddings for semantic search",
      path: "lancedb_data volume → /data/lancedb",
      configurable: false,
    },
    {
      name: "Neo4j",
      type: "Container (planned)",
      purpose: "Temporal knowledge graph — entities, relations, facts",
      path: "bolt://neo4j:7687",
      configurable: true,
      envVars: ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"],
    },
  ];

  const objectStorage = [
    {
      name: "Cloudflare R2",
      description: "S3-compatible object storage for DIAL Core file attachments and binary evidence",
      envVars: ["R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET_NAME"],
      status: "configured",
    },
    {
      name: "AWS S3",
      description: "Alternative S3 backend — same env vars, different endpoint",
      envVars: ["R2_ENDPOINT_URL (set to S3 endpoint)", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY"],
      status: "compatible",
    },
    {
      name: "Local Filesystem",
      description: "Docker volume-backed storage (default for Directus uploads, SBV data)",
      envVars: [],
      status: "active",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Evidence Storage Tiers */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Evidence Storage Tiers</h2>
        <p className="text-sm text-muted-foreground mb-4">
          Data flows through tiers in order: DuckDB (fingerprint) → PostgreSQL (structured) →
          LanceDB (vectors) → Neo4j (graph).
        </p>
        <div className="space-y-3">
          {storageTiers.map((tier) => (
            <div key={tier.name} className="rounded-lg border bg-card p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium">{tier.name}</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">{tier.purpose}</p>
                </div>
                <span className="text-xs bg-muted px-2 py-1 rounded">{tier.type}</span>
              </div>
              <div className="mt-2 flex items-center gap-2">
                <code className="text-xs text-muted-foreground font-mono">{tier.path}</code>
                {tier.configurable && tier.envVars && (
                  <span className="text-[10px] text-primary">
                    ({tier.envVars.join(", ")})
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Object / Block Storage */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Object Storage</h2>
        <p className="text-sm text-muted-foreground mb-4">
          S3-compatible storage for binary files, attachments, and large evidence blobs.
          DIAL Core uses the jclouds S3 provider configured via environment variables.
        </p>
        <div className="space-y-3">
          {objectStorage.map((store) => (
            <div key={store.name} className="rounded-lg border bg-card p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium">{store.name}</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">{store.description}</p>
                </div>
                <span
                  className={cn(
                    "text-xs rounded-full px-2 py-0.5 font-medium",
                    store.status === "active"
                      ? "bg-green-500/10 text-green-600 dark:text-green-400"
                      : store.status === "configured"
                      ? "bg-blue-500/10 text-blue-600 dark:text-blue-400"
                      : "bg-muted text-muted-foreground"
                  )}
                >
                  {store.status}
                </span>
              </div>
              {store.envVars.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {store.envVars.map((v) => (
                    <code key={v} className="text-[10px] bg-muted px-1.5 py-0.5 rounded">
                      {v}
                    </code>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Docker Volumes */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Docker Volumes</h2>
        <div className="rounded-lg border bg-card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/30">
                <th className="text-left font-medium px-4 py-2">Volume</th>
                <th className="text-left font-medium px-4 py-2">Service</th>
                <th className="text-left font-medium px-4 py-2">Mount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {[
                ["pgdata", "PostgreSQL", "/var/lib/postgresql/data"],
                ["lancedb_data", "Py MCP Server", "/data/lancedb"],
                ["ollama_models", "Ollama", "/root/.ollama"],
                ["sbv_data", "SBV", "/data"],
                ["portainer_data", "Portainer", "/data"],
                ["directus_uploads", "Directus", "/directus/uploads"],
                ["influxdb_data", "InfluxDB", "/var/lib/influxdb2"],
                ["caddy_data", "Caddy", "/data"],
                ["caddy_config", "Caddy", "/config"],
              ].map(([vol, svc, mount]) => (
                <tr key={vol} className="hover:bg-muted/30">
                  <td className="px-4 py-2 font-mono text-xs">{vol}</td>
                  <td className="px-4 py-2">{svc}</td>
                  <td className="px-4 py-2 font-mono text-xs text-muted-foreground">{mount}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Directus */}
      <div className="rounded-lg border border-dashed bg-muted/20 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold">Directus Data Surface</h3>
            <p className="text-xs text-muted-foreground mt-1">
              Directus provides a REST/GraphQL API and admin UI over PostgreSQL evidence tables.
              Opt-in service — activate with{" "}
              <code className="bg-muted px-1 py-0.5 rounded">
                docker compose --profile data up directus -d
              </code>
            </p>
          </div>
          <a
            href="http://localhost:8055"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 rounded-md border bg-card px-3 py-1.5 text-xs font-medium hover:bg-accent hover:text-accent-foreground transition-colors shrink-0"
          >
            Open Directus
            <ExternalLink className="h-3 w-3" />
          </a>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Services
// ---------------------------------------------------------------------------

function ServicesSection() {
  const services = [
    {
      name: "DIAL Chat",
      url: "http://localhost:3000",
      description: "Admin/dev AI chat — access all MCP tools via natural language",
      port: 3000,
    },
    {
      name: "DIAL Core API",
      url: "http://localhost:8080",
      description: "AI gateway — model routing, tool dispatch, config",
      port: 8080,
    },
    {
      name: "Keycloak",
      url: "http://localhost:8180",
      description: "Identity & access management — OIDC provider, user management",
      port: 8180,
    },
    {
      name: "Portainer",
      url: "http://localhost:9000",
      description: "Docker container management (also embedded in Containers page)",
      port: 9000,
    },
    {
      name: "SBV (SMS Viewer)",
      url: "http://localhost:8084",
      description: "SMS Backup & Restore XML viewer (also embedded in SMS Viewer page)",
      port: 8084,
    },
    {
      name: "Directus",
      url: "http://localhost:8055",
      description: "Data/admin surface — REST/GraphQL over evidence tables (opt-in: --profile data)",
      port: 8055,
    },
    {
      name: "Ollama",
      url: "http://localhost:11434",
      description: "Local LLM inference server",
      port: 11434,
    },
    {
      name: "InfluxDB",
      url: "http://localhost:8086",
      description: "Time-series analytics database",
      port: 8086,
    },
    {
      name: "Analytics Realtime",
      url: "http://localhost:8087",
      description: "DIAL analytics dashboard (InfluxDB-backed)",
      port: 8087,
    },
    {
      name: "Audit Logger",
      url: "http://localhost:8085",
      description: "DIAL interceptor — logs all tool calls to PostgreSQL",
      port: 8085,
    },
  ];

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        All platform services and their access points. Click to open in a new tab.
      </p>
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
              <p className="text-xs text-muted-foreground mt-0.5">{service.description}</p>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground group-hover:text-foreground transition-colors">
              <code className="text-xs bg-muted px-2 py-1 rounded">:{service.port}</code>
              <ExternalLink className="h-3.5 w-3.5" />
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// General
// ---------------------------------------------------------------------------

function GeneralSection() {
  return (
    <div className="space-y-6">
      {/* Platform Info */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Platform Info</h2>
        <div className="rounded-lg border bg-card p-4 space-y-3 text-sm">
          {[
            ["Architecture", "AI DIAL Gateway + 3 MCP Servers (TS, Py, JS)"],
            ["Evidence Pipeline", "SHA-256 → DuckDB → PostgreSQL → LanceDB → Neo4j"],
            ["Auth Provider", "Keycloak OIDC (http://localhost:8180)"],
            ["Container Management", "Portainer CE (embedded in Containers page)"],
            ["Object Storage", "Cloudflare R2 (S3-compatible) via DIAL Core"],
            ["Current Phase", "A — Foundation & Storage Tools"],
          ].map(([label, value]) => (
            <div key={label} className="flex justify-between">
              <span className="text-muted-foreground">{label}</span>
              <span className="text-right">{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* MCP Server Ports */}
      <div>
        <h2 className="text-lg font-semibold mb-4">MCP Server Endpoints</h2>
        <div className="rounded-lg border bg-card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/30">
                <th className="text-left font-medium px-4 py-2">Server</th>
                <th className="text-left font-medium px-4 py-2">Port</th>
                <th className="text-left font-medium px-4 py-2">Purpose</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {[
                ["TS MCP Server", "8081", "Parsers, DuckDB vault, PostgreSQL writes, SBV integration"],
                ["Py MCP Server", "8000", "Semantica NLP, LanceDB vectors, Neo4j graph ops"],
                ["JS MCP Server", "8083", "Legacy JS tools, Docling, Pandoc"],
              ].map(([name, port, purpose]) => (
                <tr key={name} className="hover:bg-muted/30">
                  <td className="px-4 py-2 font-medium">{name}</td>
                  <td className="px-4 py-2 font-mono text-xs">{port}</td>
                  <td className="px-4 py-2 text-muted-foreground">{purpose}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Future: Workflow Orchestration */}
      <div className="rounded-lg border border-dashed bg-muted/20 p-6 text-center">
        <h3 className="text-sm font-semibold">Workflow Orchestration (Planned)</h3>
        <p className="text-xs text-muted-foreground mt-2 max-w-md mx-auto">
          n8n or similar workflow engine for configuring ingestion pipelines, scheduled jobs,
          and multi-step evidence processing workflows. Will be embedded here when activated.
        </p>
      </div>
    </div>
  );
}
