import { Link, useRoute } from "wouter";
import {
  LayoutDashboard,
  MessageSquare,
  FileSearch,
  Smartphone,
  Settings,
  Shield,
  ExternalLink,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { path: "/", label: "Dashboard", icon: LayoutDashboard },
  { path: "/evidence", label: "Evidence", icon: FileSearch },
  { path: "/conversations", label: "Conversations", icon: MessageSquare },
  { path: "/sbv", label: "SMS Viewer", icon: Smartphone },
  { path: "/settings", label: "Settings", icon: Settings },
];

function NavItem({ path, label, icon: Icon }: (typeof navItems)[number]) {
  const [isActive] = useRoute(path === "/" ? path : `${path}/:rest*`);
  const [isExact] = useRoute(path);
  const active = path === "/" ? isExact : isActive;

  return (
    <Link
      href={path}
      className={cn(
        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
        active
          ? "bg-primary/10 text-primary"
          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
      )}
    >
      <Icon className="h-4 w-4 shrink-0" />
      <span>{label}</span>
    </Link>
  );
}

export function AppSidebar() {
  return (
    <aside className="flex h-screen w-64 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground">
      {/* Logo / Brand */}
      <div className="flex h-14 items-center gap-2 border-b border-sidebar-border px-4">
        <Shield className="h-6 w-6 text-primary" />
        <span className="text-lg font-semibold tracking-tight">
          MCP Platform
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        {navItems.map((item) => (
          <NavItem key={item.path} {...item} />
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-sidebar-border p-3">
        <a
          href="/sbv/"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 rounded-lg px-3 py-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          <ExternalLink className="h-3 w-3" />
          Open SBV in new tab
        </a>
        <div className="px-3 py-1 text-xs text-muted-foreground">
          DIAL Chat:{" "}
          <a
            href="http://localhost:3000"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-foreground"
          >
            :3000
          </a>
        </div>
      </div>
    </aside>
  );
}
