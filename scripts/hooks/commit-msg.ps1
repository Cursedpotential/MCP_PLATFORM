# =============================================================================
# MCP_PLATFORM commit-msg hook — PowerShell
# Enforces: conventional commit format, task ID presence for code changes,
#           flags approval bypass attempts, WIP gate, message length
# Usage: Called by install-hooks.ps1 shim
#        $args[0] = path to the commit message temp file
# =============================================================================
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if (-not $args -or $args.Count -eq 0) {
    Write-Host "[FAIL] commit-msg hook called without commit message file argument." -ForegroundColor Red
    exit 1
}

$COMMIT_MSG_FILE = $args[0]
if (-not (Test-Path $COMMIT_MSG_FILE)) {
    Write-Host "[FAIL] Commit message file not found: $COMMIT_MSG_FILE" -ForegroundColor Red
    exit 1
}

$MSG        = Get-Content $COMMIT_MSG_FILE -Raw
$FIRST_LINE = ($MSG -split "`n")[0].Trim()
$FAIL       = 0

function Write-Fail { param([string]$msg) Write-Host "[FAIL] $msg" -ForegroundColor Red;    $script:FAIL++ }
function Write-Warn { param([string]$msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-OK   { param([string]$msg) Write-Host "[OK]   $msg" -ForegroundColor Green }

# ─── 1. CONVENTIONAL COMMIT FORMAT ───────────────────────────────────────────
# Required: type(scope): description
# Types: feat, fix, chore, docs, refactor, test, style, ci, perf, revert, wip
$CONV_PATTERN = '^(feat|fix|chore|docs|refactor|test|style|ci|perf|revert|wip)(\([a-zA-Z0-9_/\-]+\))?(!)?:\s.+'

if ($FIRST_LINE -notmatch $CONV_PATTERN) {
    Write-Fail "Commit message must follow conventional commit format."
    Write-Host "  Got:      $FIRST_LINE" -ForegroundColor Yellow
    Write-Host "  Expected: type(scope): description" -ForegroundColor Yellow
    Write-Host "  Types: feat | fix | chore | docs | refactor | test | style | ci | perf | revert | wip" -ForegroundColor Yellow
    Write-Host "  Example:  feat(ts-mcp-server): implement facebook parser" -ForegroundColor Yellow
} else {
    Write-OK "Conventional commit format OK"
}

# ─── 2. TASK ID PRESENCE (warn, not fail) ─────────────────────────────────────
$TASK_PATTERN = 'PLAT-\d+|OQ-[0-9A-Z]+|OQ-C\d+|ADR-\d+|GATE-LIFTED|hotfix|chore'
if ($MSG -notmatch $TASK_PATTERN) {
    Write-Warn "No task ID found (PLAT-NNN, OQ-NNN, ADR-NNN). Consider adding one."
    Write-Host "  Example: feat(ts-mcp-server): implement facebook parser [PLAT-001]" -ForegroundColor Yellow
} else {
    Write-OK "Task ID present"
}

# ─── 3. APPROVAL BYPASS DETECTION ─────────────────────────────────────────────
$BYPASS_PATTERN  = 'approved|looks good|sign[\s\-]?off|lgtm|ok to merge|green[\s\-]?light'
$EXACT_APPROVAL  = 'approved — proceed'

if ($MSG -imatch $BYPASS_PATTERN) {
    # Check if the exact approval phrase is present — if so, it's legitimate
    if ($MSG -notlike "*$EXACT_APPROVAL*") {
        Write-Warn "Approval language detected in commit message."
        Write-Host "  Only 'approved — proceed' is valid approval. Other phrases are not approval." -ForegroundColor Yellow
    }
}

# ─── 4. WIP GATE ──────────────────────────────────────────────────────────────
if ($FIRST_LINE -imatch '^wip[:(]') {
    Write-Warn "WIP commit — will be blocked by pre-push if pushing to main."
}

# ─── 5. MESSAGE LENGTH ────────────────────────────────────────────────────────
$msgLen = $FIRST_LINE.Length
if ($msgLen -gt 100) {
    Write-Warn "First line is $msgLen chars. Keep under 100 for readability in git log."
}
if ($msgLen -lt 10) {
    Write-Fail "Commit message too short: '$FIRST_LINE'"
}

# ─── RESULT ───────────────────────────────────────────────────────────────────
if ($FAIL -gt 0) {
    Write-Host ""
    Write-Host "commit-msg FAILED — amend your commit message." -ForegroundColor Red
    Write-Host "Format: type(scope): description [TASK-ID]"
    exit 1
}

Write-OK "commit-msg passed"
exit 0
