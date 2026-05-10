#!/bin/bash
# Session start hook for Claude Code on the web.
# Installs dependencies for all subprojects so tests/linters work immediately.
# Skipped on local sessions to avoid surprising the developer's environment.

set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

REPO="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$REPO"

log() { echo "[session-start] $*"; }

install_npm() {
  local dir="$1"
  if [ -f "$dir/package.json" ]; then
    log "npm install in $dir"
    (cd "$dir" && npm install --no-audit --no-fund --loglevel=error)
  fi
}

install_pip() {
  local dir="$1"
  if [ -f "$dir/requirements.txt" ]; then
    log "pip install in $dir"
    (cd "$dir" && pip install --quiet --disable-pip-version-check -r requirements.txt)
  fi
}

# Frontend + MCP servers (Node)
install_npm "client"
install_npm "mcp-servers/ts-mcp-server"
install_npm "mcp-servers/js-mcp-server"
install_npm "infrastructure/interceptors/audit_logger"

# Python MCP server + interceptor
install_pip "mcp-servers/py-mcp-server"
install_pip "infrastructure/interceptors/audit_logger"

log "done"
