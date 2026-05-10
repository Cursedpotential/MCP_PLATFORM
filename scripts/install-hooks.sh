#!/usr/bin/env sh
# =============================================================================
# MCP_PLATFORM install-hooks.sh — one-command hook installer (bash)
# Installs all Git hooks from scripts/hooks/ into .git/hooks/
# Idempotent — safe to re-run.
# Usage: bash scripts/install-hooks.sh [--dry-run]
# =============================================================================
set -eu

REPO_ROOT=$(git rev-parse --show-toplevel)
HOOKS_SRC="$REPO_ROOT/scripts/hooks"
HOOKS_DEST="$REPO_ROOT/.git/hooks"
DRY_RUN=0

RED='\033[0;31m'
GRN='\033[0;32m'
YEL='\033[0;33m'
NC='\033[0m'

for arg in "$@"; do
  [ "$arg" = "--dry-run" ] && DRY_RUN=1
done

fail() { printf "${RED}[FAIL]${NC} %s\n" "$1"; exit 1; }
info() { printf "${GRN}[OK]${NC}   %s\n" "$1"; }
warn() { printf "${YEL}[WARN]${NC} %s\n" "$1"; }
dry()  { printf "${YEL}[DRY]${NC}  Would %s\n" "$1"; }

echo "────────────────────────────────────────────"
echo " MCP_PLATFORM hook installer"
[ "$DRY_RUN" -eq 1 ] && echo " (DRY RUN — no changes will be made)"
echo "────────────────────────────────────────────"

# Verify hooks source directory exists
[ -d "$HOOKS_SRC" ] || fail "Hook sources not found at $HOOKS_SRC"
[ -d "$HOOKS_DEST" ] || fail ".git/hooks directory not found — is this a git repo?"

# ── Install bash hooks ────────────────────────────────────────────────────────
for HOOK in pre-commit pre-push commit-msg; do
  SRC="$HOOKS_SRC/$HOOK"
  DEST="$HOOKS_DEST/$HOOK"

  [ -f "$SRC" ] || { warn "Source not found: $SRC — skipping"; continue; }

  if [ "$DRY_RUN" -eq 1 ]; then
    dry "install $HOOK → $DEST"
    continue
  fi

  # Backup existing hook if it's not ours
  if [ -f "$DEST" ] && ! grep -q "MCP_PLATFORM" "$DEST" 2>/dev/null; then
    cp "$DEST" "$DEST.bak"
    warn "Backed up existing $HOOK to $HOOK.bak"
  fi

  cp "$SRC" "$DEST"
  chmod +x "$DEST"
  info "Installed: $HOOK"
done

# ── Install PowerShell shims (for Windows/WSL) ────────────────────────────────
# Git on Windows with PowerShell hooks needs a thin sh shim that delegates to .ps1
for HOOK in pre-commit pre-push commit-msg; do
  PS1_SRC="$HOOKS_SRC/${HOOK}.ps1"
  SHIM="$HOOKS_DEST/${HOOK}"  # The sh shim IS the hook — delegates to .ps1

  [ -f "$PS1_SRC" ] || { warn "PS1 source not found: $PS1_SRC — skipping shim"; continue; }

  # The bash hook already handles Linux/macOS. The .ps1 lives next to the bash
  # hook in scripts/hooks/ and is called by the bash hook on Windows if pwsh is available.
  # No separate shim needed — the bash hook auto-detects and delegates.
  [ "$DRY_RUN" -eq 0 ] && info "PS1 hook available: ${HOOK}.ps1 (called by bash hook when pwsh detected)"
done

# ── Validate installation ─────────────────────────────────────────────────────
if [ "$DRY_RUN" -eq 0 ]; then
  echo ""
  echo "Installed hooks:"
  for HOOK in pre-commit pre-push commit-msg; do
    DEST="$HOOKS_DEST/$HOOK"
    if [ -f "$DEST" ] && [ -x "$DEST" ]; then
      info "$HOOK — executable ✓"
    else
      warn "$HOOK — NOT found or not executable"
    fi
  done

  echo ""
  echo "Hooks installed. Test with:"
  echo "  git diff --cached | head     # see what pre-commit would scan"
  echo "  bash scripts/check-guardrails.sh --staged"
fi

echo "────────────────────────────────────────────"
printf "${GRN}Hook installation complete.${NC}\n"
exit 0
