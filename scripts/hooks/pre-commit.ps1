# =============================================================================
# MCP_PLATFORM pre-commit hook — PowerShell
# Enforces: no stubs, no DIAL references in new code, no hardcoded secrets,
#           no deleted files (must use _DEPRECATED/), no Agno/n8n refs,
#           CONDUCTOR GATE check on workflow definitions
# Usage: git config core.hooksPath scripts/hooks
#        On Windows, Git will call pre-commit.ps1 if pre-commit is absent or
#        you can add a thin shim — see scripts/install-hooks.ps1
# =============================================================================
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$FAIL  = 0
$WARNS = 0

function Write-Fail  { param([string]$msg) Write-Host "[FAIL] $msg" -ForegroundColor Red;    $script:FAIL++ }
function Write-Warn  { param([string]$msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow; $script:WARNS++ }
function Write-OK    { param([string]$msg) Write-Host "[OK]   $msg" -ForegroundColor Green }

Write-Host "--------------------------------------------"
Write-Host " MCP_PLATFORM pre-commit guardrails"
Write-Host "--------------------------------------------"

# Staged files (added, copied, modified — not deleted)
$staged = git diff --cached --name-only --diff-filter=ACM 2>$null
if (-not $staged) {
    Write-OK "No staged files — nothing to check"
    exit 0
}

# ─── 1. STUB CHECK ────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[ 1/6 ] Checking for stubs..."

$stubPatterns = @(
    'TODO:',
    'FIXME:',
    'throw new Error\("not implemented"\)',
    "throw new Error\('not implemented'\)",
    '# TODO',
    '# FIXME',
    'NotImplementedError',
    'raise NotImplementedError',
    'pass\s*#\s*(stub|TODO|placeholder)'
)
$stubRegex = ($stubPatterns | ForEach-Object { "(?:$_)" }) -join '|'

$sourceExts    = @('.ts', '.tsx', '.js', '.py', '.sh')
$excludePaths  = @('_DEPRECATED/', 'docs/wiki/archive/')
$stubFound     = $false

foreach ($f in $staged) {
    $ext = [System.IO.Path]::GetExtension($f)
    if ($sourceExts -notcontains $ext) { continue }
    $skip = $false
    foreach ($ex in $excludePaths) { if ($f -like "$ex*") { $skip = $true; break } }
    if ($skip) { continue }

    $content = git show ":$f" 2>$null
    if (-not $content) { continue }
    $lines = $content -split "`n"
    $lineNum = 0
    foreach ($line in $lines) {
        $lineNum++
        if ($line -match $stubRegex) {
            Write-Fail "Stub pattern in ${f}:$lineNum — $($line.Trim())"
            $stubFound = $true
        }
    }
}
if (-not $stubFound) { Write-OK "No stubs found" }

# ─── 2. DIAL REFERENCE CHECK ─────────────────────────────────────────────────
Write-Host ""
Write-Host "[ 2/6 ] Checking for DIAL references in new code..."

$dialPattern = 'ai-dial-core|dial-chat|dial-stack|epam/ai-dial|ai\.dial\.core|aidial\.'
$dialExts    = @('.ts', '.tsx', '.js', '.py', '.sh', '.yml', '.yaml', '.json')
$dialExclude = @('_DEPRECATED/', 'docs/wiki/archive/', 'DECISION_REGISTER', 'ADR')
$dialFound   = $false

foreach ($f in $staged) {
    $ext = [System.IO.Path]::GetExtension($f)
    if ($dialExts -notcontains $ext) { continue }
    $skip = $false
    foreach ($ex in $dialExclude) { if ($f -like "*$ex*") { $skip = $true; break } }
    if ($skip) { continue }

    $content = git show ":$f" 2>$null
    if (-not $content) { continue }
    $lines = $content -split "`n"
    $lineNum = 0
    foreach ($line in $lines) {
        $lineNum++
        if ($line -imatch $dialPattern) {
            Write-Fail "DIAL ref (deprecated per ADR-033) in ${f}:$lineNum — $($line.Trim())"
            $dialFound = $true
        }
    }
}
if (-not $dialFound) { Write-OK "No DIAL references in active code" }

# ─── 3. SECRET CHECK ──────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[ 3/6 ] Checking for secrets..."

$secretRules = @(
    @{ Pattern = 'gsk_[A-Za-z0-9]{20,}';                                 Label = 'Groq API key' },
    @{ Pattern = 'sk-[A-Za-z0-9]{32,}';                                  Label = 'OpenAI-style API key' },
    @{ Pattern = 'AIza[0-9A-Za-z\-_]{35}';                               Label = 'Google API key' },
    @{ Pattern = 'CONDUCTOR_AUTH_SECRET\s*=\s*["''][^"''$\{]{8,}';       Label = 'Conductor auth secret hardcoded' },
    @{ Pattern = '-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY-----';     Label = 'Private key material' },
    @{ Pattern = 'password\s*[:=]\s*["''][^"''$\{]{6,}';                 Label = 'Hardcoded password' }
)
$secretExclude = @('.env', '.pem', '.key')
$secretFound   = $false

foreach ($f in $staged) {
    $ext = [System.IO.Path]::GetExtension($f)
    if ($secretExclude -contains $ext) { continue }
    $content = git show ":$f" 2>$null
    if (-not $content) { continue }
    $lines = $content -split "`n"
    $lineNum = 0
    foreach ($line in $lines) {
        $lineNum++
        foreach ($rule in $secretRules) {
            if ($line -match $rule.Pattern) {
                Write-Fail "Possible $($rule.Label) in ${f}:$lineNum"
                $secretFound = $true
            }
        }
    }
}
if (-not $secretFound) { Write-OK "No secrets detected" }

# ─── 4. DELETED FILES CHECK ───────────────────────────────────────────────────
Write-Host ""
Write-Host "[ 4/6 ] Checking for deleted files..."

$deleted = git diff --cached --name-only --diff-filter=D 2>$null
$allowedDelExt = @('.pyc', '.pyo', '.tsbuildinfo')
$deleteFound = $false

if ($deleted) {
    foreach ($f in $deleted) {
        $ext = [System.IO.Path]::GetExtension($f)
        if ($allowedDelExt -contains $ext) { continue }
        if ($f -like '__pycache__/*' -or $f -like 'dist/*' -or $f -like 'build/*') { continue }
        Write-Fail "File deletion detected: $f"
        Write-Host "       Move to _DEPRECATED/$f instead of deleting." -ForegroundColor Yellow
        $deleteFound = $true
    }
}
if (-not $deleteFound) { Write-OK "No file deletions" }

# ─── 5. CONDUCTOR GATE CHECK ─────────────────────────────────────────────────
Write-Host ""
Write-Host "[ 5/6 ] Checking CONDUCTOR GATE..."

$gateFound = $false
foreach ($f in $staged) {
    if ($f -match '(?:workflows|workflow-definitions)[/\\][^/\\]+\.json$') {
        $content = git show ":$f" 2>$null
        if ($content -and ($content -notmatch 'GATE-LIFTED')) {
            Write-Fail "No GATE-LIFTED marker in workflow definition: $f"
            Write-Host "       Add '// GATE-LIFTED: <date> <approver>' before committing workflow definitions." -ForegroundColor Yellow
            $gateFound = $true
        } else {
            Write-OK "GATE-LIFTED marker found: $f"
        }
    }
}
if (-not $gateFound) { Write-OK "Conductor gate check passed" }

# ─── 6. AGNO / N8N REFERENCE CHECK ───────────────────────────────────────────
Write-Host ""
Write-Host "[ 6/6 ] Checking for removed component references (Agno, n8n)..."

$removedPattern = 'import.*agno|from agno|require.*agno|agno\.Agent|n8n_webhook|n8n\.workflow|n8nWorkflow'
$removedExts    = @('.ts', '.tsx', '.js', '.py')
$removedExclude = @('_DEPRECATED/', 'docs/wiki/archive/', 'DECISION_REGISTER')
$removedFound   = $false

foreach ($f in $staged) {
    $ext = [System.IO.Path]::GetExtension($f)
    if ($removedExts -notcontains $ext) { continue }
    $skip = $false
    foreach ($ex in $removedExclude) { if ($f -like "*$ex*") { $skip = $true; break } }
    if ($skip) { continue }

    $content = git show ":$f" 2>$null
    if (-not $content) { continue }
    $lines = $content -split "`n"
    $lineNum = 0
    foreach ($line in $lines) {
        $lineNum++
        if ($line -imatch $removedPattern) {
            Write-Fail "Removed component ref (Agno/n8n per ADR-033) in ${f}:$lineNum — $($line.Trim())"
            $removedFound = $true
        }
    }
}
if (-not $removedFound) { Write-OK "No removed component references" }

# ─── RESULT ───────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "--------------------------------------------"
if ($FAIL -gt 0) {
    Write-Host "pre-commit FAILED — fix the issues above before committing." -ForegroundColor Red
    Write-Host "Run scripts/check-guardrails.ps1 for a full standalone report."
    exit 1
}
if ($WARNS -gt 0) {
    Write-Host "pre-commit passed with $WARNS warning(s) — review above." -ForegroundColor Yellow
    exit 0
}
Write-Host "pre-commit passed." -ForegroundColor Green
exit 0
