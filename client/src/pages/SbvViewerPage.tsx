import { ExternalLink, Maximize2, Minimize2 } from "lucide-react";
import { useState } from "react";

/**
 * SBV Viewer page — embeds the SBV (SMS Backup Viewer) web UI as an iframe.
 *
 * SBV is served by Caddy at /sbv/ (reverse-proxied from sbv:8081).
 * This gives a seamless all-in-one app feel — SBV looks like a native page
 * within the MCP Platform rather than a separate tool on another port.
 */
export function SbvViewerPage() {
  const [isFullscreen, setIsFullscreen] = useState(false);

  // In Docker Compose, Caddy reverse-proxies /sbv/ → sbv:8081.
  // For local dev, fall back to the direct port.
  const sbvUrl = "/sbv/";

  return (
    <div className={`flex flex-col ${isFullscreen ? "fixed inset-0 z-50 bg-background" : "h-full"}`}>
      {/* Toolbar */}
      <div className="flex items-center justify-between border-b bg-card px-4 py-2">
        <div className="flex items-center gap-3">
          <h1 className="text-sm font-semibold">SMS Backup Viewer</h1>
          <span className="rounded-full bg-green-500/10 px-2 py-0.5 text-xs font-medium text-green-600 dark:text-green-400">
            Connected
          </span>
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
            href={sbvUrl}
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
          src={sbvUrl}
          title="SMS Backup Viewer"
          className="absolute inset-0 h-full w-full border-0"
          sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
        />
      </div>
    </div>
  );
}
