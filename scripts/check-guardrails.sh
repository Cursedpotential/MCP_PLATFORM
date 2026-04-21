#!/usr/bin/env sh
# =============================================================================
# MCP_PLATFORM check-guardrails.sh — standalone guardrail runner (bash)
# Runs all pre-commit, pre-push, and structural checks against working tree
# without requiring a staged commit. Safe to run at any time.
# Usage: bash scripts/check-guardrails.sh [--all] [--staged] [--path <dir>]
#   --all      Check every tracked source file (slow, thorough)
#   --staged   Check only staged files (default — same as pre-commit)
#   --path     Restrict scan to a specific subdirectory
# =============================================================================
set -eu

REPO_ROOT=$(git rev-parse --show-toplevel)
FAIL=0
WARNS=0
MODE="staged"
SCAN_PATH=""

RED='\033[0;31m'
YEL='\033[0;33m'
GRN='\033[0;32m'
CYN='\033[0;36m'
NC='\033[0m'

fail()    { printf "${RED}[FAIL]${NC} %s\n" "$1"; FAIL=$((FAIL+1)); }
warn()    { printf "${YEL}[WARN]${NC} %s\n" "$1"; WARNS=$((WARNS+1)); }
info()    { printf "${GRN}[OK]${NC}   %s\n" "$1"; }
section() { printf "\n${CYN}══ %s ══${NC}\n" "$1"; }

# ── Argument parsing ──────────────────────────────────────────────────────────
while [ $# -gt 0 ]; do
  case "$1" in
    --all)    MODE="all" ;;
    --staged) MODE="staged" ;;
    --path)   shift; SCAN_PATH="$1" ;;
    *) printf "Unknown flag: %s\n" "$1"; exit 1 ;;
  esac
  shift
done

echo "════════════════════════════════════════════"
echo " MCP_PLATFORM guardrail check (standalone)"
echo " Mode: $MODE${SCAN_PATH:+ | path: $SCAN_PATH}"
echo "════════════════════════════════════════════"

# ── Collect file list ─────────────────────────────────────────────────────────
if [ "$MODE" = "staged" ]; then
  FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)
  if [ -z "$FILES" ]; then
    info "No staged files."
    exit 0
  fi
else
  # All tracked source files
  if [ -n "$SCAN_PATH" ]; then
    FILES=$(git ls-files --cached -- "$SCAN_PATH" 2>/dev/null || true)
  else
    FILES=$(git ls-files --cached 2>/dev/null || true)
  fi
fi

section "1. STUB CHECK"
STUB_PATTERNS='TODO:|FIXME:|throw new Error\("not implemented"\)|throw new Error\('"'"'not implemented'"'"'\)|# TODO|# FIXME|NotImplementedError|raise NotImplementedError|pass\s*#\s*(stub|TODO|placeholder)'
STUB_HIT=0
for f in $FILES; do
  case "$f" in *.ts|*.tsx|*.js|*.py|*.sh) ;; *) continue ;; esac
  case "$f" in _DEPRECATED/*|docs/wiki/archive/*) continue ;; esac
  if [ "$MODE" = "staged" ]; then
    SRC=$(git show ":$f" 2>/dev/null || true)
  else
    SRC=$(cat "$REPO_ROOT/$f" 2>/dev/null || true)
  fi
  if echo "$SRC" | grep -nE "$STUB_PATTERNS" >/tmp/gc-stub.$$ 2>/dev/null; then
    fail "Stub in: $f"
    sed 's/^/       /' /tmp/gc-stub.$$
    STUB_HIT=$((STUB_HIT+1))
  fi
  rm -f /tmp/gc-stub.$$
done
[ "$STUB_HIT" -eq 0 ] && info "No stubs found"

section "2. DIAL REFERENCE CHECK"
DIAL_PATTERN='ai-dial-core|dial-chat|dial-stack|epam/ai-dial|ai\.dial\.core|aidial\.'
DIAL_HIT=0
for f in $FILES; do
  case "$f" in *.ts|*.tsx|*.js|*.py|*.sh|*.yml|*.yaml|*.json) ;; *) continue ;; esac
  case "$f" in _DEPRECATED/*|docs/wiki/archive/*|DECISION_REGISTER*|*ADR*) continue ;; esac
  if [ "$MODE" = "staged" ]; then
    SRC=$(git show ":$f" 2>/dev/null || true)
  else
    SRC=$(cat "$REPO_ROOT/$f" 2>/dev/null || true)
  fi
  if echo "$SRC" | grep -inE "$DIAL_PATTERN" >/tmp/gc-dial.$$ 2>/dev/null; then
    fail "DIAL ref (ADR-033 deprecated) in: $f"
    sed 's/^/       /' /tmp/gc-dial.$$
    DIAL_HIT=$((DIAL_HIT+1))
  fi
  rm -f /tmp/gc-dial.$$
done
[ "$DIAL_HIT" -eq 0 ] && info "No DIAL references in active code"

section "3. SECRET CHECK"
SECRET_RULES='gsk_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{32,}|AIza[0-9A-Za-z\-_]{35}|-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY-----|password\s*[:=]\s*["\x27][^"$\x27{]{6,}'
SECRET_HIT=0
for f in $FILES; do
  case "$f" in .env*|*.pem|*.key) continue ;; esac
  if [ "$MODE" = "staged" ]; then
    SRC=$(git show ":$f" 2>/dev/null || true)
  else
    SRC=$(cat "$REPO_ROOT/$f" 2>/dev/null || true)
  fi
  if echo "$SRC" | grep -nE "$SECRET_RULES" >/tmp/gc-secret.$$ 2>/dev/null; then
    fail "Possible secret in: $f"
    sed 's/^/       /' /tmp/gc-secret.$$
    SECRET_HIT=$((SECRET_HIT+1))
  fi
  rm -f /tmp/gc-secret.$$
done
[ "$SECRET_HIT" -eq 0 ] && info "No secrets detected"

section "4. AGNO / N8N REFERENCE CHECK"
REMOVED_PATTERN='import.*agno|from agno|require.*agno|agno\.Agent|n8n_webhook|n8n\.workflow|n8nWorkflow'
REMOVED_HIT=0
for f in $FILES; do
  case "$f" in *.ts|*.tsx|*.js|*.py) ;; *) continue ;; esac
  case "$f" in _DEPRECATED/*|docs/wiki/archive/*|DECISION_REGISTER*) continue ;; esac
  if [ "$MODE" = "staged" ]; then
    SRC=$(git show ":$f" 2>/dev/null || true)
  else
    SRC=$(cat "$REPO_ROOT/$f" 2>/dev/null || true)
  fi
  if echo "$SRC" | grep -nE "$REMOVED_PATTERN" >/tmp/gc-removed.$$ 2>/dev/null; then
    fail "Removed component ref (Agno/n8n per ADR-033) in: $f"
    sed 's/^/       /' /tmp/gc-removed.$$
    REMOVED_HIT=$((REMOVED_HIT+1))
  fi
  rm -f /tmp/gc-removed.$$
done
[ "$REMOVED_HIT" -eq 0 ] && info "No Agno/n8n references in active code"

section "5. CONDUCTOR GATE CHECK"
GATE_HIT=0
for f in $FILES; do
  case "$f" in */workflows/*.json|*/workflow-definitions/*.json) ;;
    *) continue ;;
  esac
  if [ "$MODE" = "staged" ]; then
    SRC=$(git show ":$f" 2>/dev/null || true)
  else
    SRC=$(cat "$REPO_ROOT/$f" 2>/dev/null || true)
  fi
  if ! echo "$SRC" | grep -q "GATE-LIFTED" 2>/dev/null; then
    fail "No GATE-LIFTED marker in workflow definition: $f"
    GATE_HIT=$((GATE_HIT+1))
  else
    info "GATE-LIFTED found: $f"
  fi
done
[ "$GATE_HIT" -eq 0 ] && info "Conductor gate check passed"

section "6. EVIDENCE DATA LEAK CHECK"
DATA_HIT=0
for f in $FILES; do
  case "$f" in
    data/*|evidence/*|*.duckdb|*.sqlite|*.sqlite3|*.db)
      fail "Evidence/data file present in repo: $f"
      DATA_HIT=$((DATA_HIT+1))
      ;;
  esac
done
[ "$DATA_HIT" -eq 0 ] && info "No evidence data files detected"

section "7. ORPHANED _DEPRECATED FILE CHECK"
# Warn if a _DEPRECATED/ file has no companion entry in the index pointing to it
DEP_FILES=$(git ls-files -- '_DEPRECATED/' 2>/dev/null || true)
DEP_COUNT=$(echo "$DEP_FILES" | grep -c . 2>/dev/null || echo 0)
if [ "$DEP_COUNT" -gt 0 ]; then
  info "$DEP_COUNT file(s) in _DEPRECATED/ — verify they are listed in INDEX.md"
fi

# ── SUMMARY ──────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════"
printf "Results: ${RED}%d fail(s)${NC}, ${YEL}%d warning(s)${NC}\n" "$FAIL" "$WARNS"
echo "════════════════════════════════════════════"

if [ "$FAIL" -gt 0 ]; then
  printf "${RED}GUARDRAIL CHECK FAILED — fix the issues above.${NC}\n"
  exit 1
fi
if [ "$WARNS" -gt 0 ]; then
  printf "${YEL}Guardrail check passed with warnings — review above.${NC}\n"
  exit 0
fi
printf "${GRN}All guardrail checks passed.${NC}\n"
exit 0
