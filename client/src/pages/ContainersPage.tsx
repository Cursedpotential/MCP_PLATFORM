import { ExternalLink, Maximize2, Minimize2, Container } from "lucide-react";
import { useState } from "react";

/**
 * Containers page — embeds Dockhand as an iframe for Docker container management.
 *
 * Dockhand is served by Caddy at /dockhand/ (reverse-proxied from dockhand:3000).
 * Lightweight, open-source Docker management UI with real-time controls,
 * vulnerability scanning, compose stack editing, and container terminal access.
 *
 * On first access, Dockhand will ask you to create an admin account.
 * Supports OIDC/SSO — can integrate with our Keycloak for auth.
 */
export function ContainersPage() {
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Caddy reverse-proxies /dockhand/ → dockhand:3000
  // Direct access also available at http://localhost:3007
  const dockhandUrl = "/dockhand/";

  return (
    <div className={`flex flex-col ${isFullscreen ? "fixed inset-0 z-50 bg-background" : "h-full"}`}>
      {/* Toolbar */}
      <div className="flex items-center justify-between border-b bg-card px-4 py-2">
        <div className="flex items-center gap-3">
          <Container className="h-4 w-4 text-muted-foreground" />
          <h1 className="text-sm font-semibold">Container Management</h1>
          <span className="text-xs text-muted-foreground">Dockhand</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
            title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
          >
            {isFullscreen ? (
              <Minimize2 className="h-3.5 w-3.5" />
            ) : (
              <Maximize2 className="h-3.5 w-3.5" />
            )}
            {isFullscreen ? "Exit" : "Expand"}
          </button>
          <a
            href={dockhandUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            <ExternalLink className="h-3.5 w-3.5" />
            Open in new tab
          </a>
        </div>
      </div>

      {/* Iframe */}
      <div className="flex-1 relative">
        <iframe
          src={dockhandUrl}
          title="Dockhand — Container Management"
          className="absolute inset-0 h-full w-full border-0"
          sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-popups-to-escape-sandbox"
        />
      </div>
    </div>
  );
}
