# =============================================================================
# MCP_PLATFORM check-guardrails.ps1 — standalone guardrail runner (PowerShell)
# Runs all pre-commit, pre-push, and structural checks against working tree.
# Usage: .\scripts\check-guardrails.ps1 [-Mode staged|all] [-Path <subdir>]
#   -Mode staged   Check only staged files (default)
#   -Mode all      Check every tracked source file
#   -Path          Restrict scan to a specific subdirectory
# =============================================================================
[CmdletBinding()]
param(
    [ValidateSet('staged','all')]
    [string]$Mode = 'staged',
    [string]$ScanPath = ''
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$FAIL  = 0
$WARNS = 0

function Write-Fail    { param([string]$msg) Write-Host "[FAIL] $msg" -ForegroundColor Red;    $script:FAIL++ }
function Write-Warn    { param([string]$msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow; $script:WARNS++ }
function Write-OK      { param([string]$msg) Write-Host "[OK]   $msg" -ForegroundColor Green }
function Write-Section { param([string]$msg) Write-Host "`n══ $msg ══" -ForegroundColor Cyan }

Write-Host "============================================"
Write-Host " MCP_PLATFORM guardrail check (standalone)"
Write-Host " Mode: $Mode$(if ($ScanPath) { " | path: $ScanPath" })"
Write-Host "============================================"

# ── Collect file list ─────────────────────────────────────────────────────────
if ($Mode -eq 'staged') {
    $files = (git diff --cached --name-only --diff-filter=ACM 2>$null) -split "`n" | Where-Object { $_ }
    if (-not $files) {
        Write-OK "No staged files."
        exit 0
    }
} else {
    $gitArgs = @('ls-files', '--cached')
    if ($ScanPath) { $gitArgs += '--'; $gitArgs += $ScanPath }
    $files = (git @gitArgs 2>$null) -split "`n" | Where-Object { $_ }
}

function Get-FileContent {
    param([string]$f, [string]$mode)
    if ($mode -eq 'staged') {
        return git show ":$f" 2>$null
    } else {
        $fullPath = Join-Path (git rev-parse --show-toplevel) $f
        if (Test-Path $fullPath) { return Get-Content $fullPath -Raw }
        return $null
    }
}

$sourceExts  = @('.ts', '.tsx', '.js', '.py', '.sh')
$codeExts    = @('.ts', '.tsx', '.js', '.py', '.sh', '.yml', '.yaml', '.json')
$excludePaths = @('_DEPRECATED/', 'docs/wiki/archive/')
$adrExclude  = @('_DEPRECATED/', 'docs/wiki/archive/', 'DECISION_REGISTER', 'ADR')

# ─── 1. STUB CHECK ────────────────────────────────────────────────────────────
Write-Section "1. STUB CHECK"
$stubRegex = 'TODO:|FIXME:|throw new Error\("not implemented"\)|NotImplementedError|raise NotImplementedError|pass\s*#\s*(stub|TODO|placeholder)'
$stubHit = $false

foreach ($f in $files) {
    $ext = [System.IO.Path]::GetExtension($f)
    if ($sourceExts -notcontains $ext) { continue }
    $skip = $false
    foreach ($ex in $excludePaths) { if ($f -like "*$ex*") { $skip = $true; break } }
    if ($skip) { continue }

    $content = Get-FileContent -f $f -mode $Mode
    if (-not $content) { continue }
    $lines = $content -split "`n"
    $lineNum = 0
    foreach ($ln in $lines) {
        $lineNum++
        if ($ln -match $stubRegex) {
            Write-Fail "Stub in ${f}:$lineNum — $($ln.Trim())"
            $stubHit = $true
        }
    }
}
if (-not $stubHit) { Write-OK "No stubs found" }

# ─── 2. DIAL REFERENCE CHECK ──────────────────────────────────────────────────
Write-Section "2. DIAL REFERENCE CHECK"
$dialPattern = 'ai-dial-core|dial-chat|dial-stack|epam/ai-dial|aidial\.'
$dialHit = $false

foreach ($f in $files) {
    $ext = [System.IO.Path]::GetExtension($f)
    if ($codeExts -notcontains $ext) { continue }
    $skip = $false
    foreach ($ex in $adrExclude) { if ($f -like "*$ex*") { $skip = $true; break } }
    if ($skip) { continue }

    $content = Get-FileContent -f $f -mode $Mode
    if (-not $content) { continue }
    $lines = $content -split "`n"
    $lineNum = 0
    foreach ($ln in $lines) {
        $lineNum++
        if ($ln -imatch $dialPattern) {
            Write-Fail "DIAL ref (ADR-033 deprecated) in ${f}:$lineNum"
            $dialHit = $true
        }
    }
}
if (-not $dialHit) { Write-OK "No DIAL references in active code" }

# ─── 3. SECRET CHECK ──────────────────────────────────────────────────────────
Write-Section "3. SECRET CHECK"
$secretRules = @(
    @{ Pattern = 'gsk_[A-Za-z0-9]{20,}';                                Label = 'Groq API key' },
    @{ Pattern = 'sk-[A-Za-z0-9]{32,}';                                 Label = 'OpenAI-style API key' },
    @{ Pattern = 'AIza[0-9A-Za-z\-_]{35}';                              Label = 'Google API key' },
    @{ Pattern = '-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY-----';    Label = 'Private key material' },
    @{ Pattern = 'password\s*[:=]\s*["''][^"''$\{]{6,}';                Label = 'Hardcoded password' }
)
$secretExclude = @('.env', '.pem', '.key')
$secretHit = $false

foreach ($f in $files) {
    $ext = [System.IO.Path]::GetExtension($f)
    if ($secretExclude -contains $ext) { continue }
    $content = Get-FileContent -f $f -mode $Mode
    if (-not $content) { continue }
    $lines = $content -split "`n"
    $lineNum = 0
    foreach ($ln in $lines) {
        $lineNum++
        foreach ($rule in $secretRules) {
            if ($ln -match $rule.Pattern) {
                Write-Fail "Possible $($rule.Label) in ${f}:$lineNum"
                $secretHit = $true
            }
        }
    }
}
if (-not $secretHit) { Write-OK "No secrets detected" }

# ─── 4. AGNO / N8N REFERENCE CHECK ───────────────────────────────────────────
Write-Section "4. AGNO / N8N REFERENCE CHECK"
$removedPattern = 'import.*agno|from agno|require.*agno|agno\.Agent|n8n_webhook|n8n\.workflow|n8nWorkflow'
$removedExts    = @('.ts', '.tsx', '.js', '.py')
$removedHit     = $false

foreach ($f in $files) {
    $ext = [System.IO.Path]::GetExtension($f)
    if ($removedExts -notcontains $ext) { continue }
    $skip = $false
    foreach ($ex in @('_DEPRECATED/', 'docs/wiki/archive/', 'DECISION_REGISTER')) {
        if ($f -like "*$ex*") { $skip = $true; break }
    }
    if ($skip) { continue }

    $content = Get-FileContent -f $f -mode $Mode
    if (-not $content) { continue }
    $lines = $content -split "`n"
    $lineNum = 0
    foreach ($ln in $lines) {
        $lineNum++
        if ($ln -imatch $removedPattern) {
            Write-Fail "Removed component ref (Agno/n8n per ADR-033) in ${f}:$lineNum"
            $removedHit = $true
        }
    }
}
if (-not $removedHit) { Write-OK "No Agno/n8n references in active code" }

# ─── 5. CONDUCTOR GATE CHECK ─────────────────────────────────────────────────
Write-Section "5. CONDUCTOR GATE CHECK"
$gateHit = $false
foreach ($f in $files) {
    if ($f -match '(?:workflows|workflow-definitions)[/\\][^/\\]+\.json$') {
        $content = Get-FileContent -f $f -mode $Mode
        if ($content -and ($content -notmatch 'GATE-LIFTED')) {
            Write-Fail "No GATE-LIFTED marker in workflow definition: $f"
            $gateHit = $true
        } else {
            Write-OK "GATE-LIFTED found: $f"
        }
    }
}
if (-not $gateHit) { Write-OK "Conductor gate check passed" }

# ─── 6. EVIDENCE DATA LEAK CHECK ─────────────────────────────────────────────
Write-Section "6. EVIDENCE DATA LEAK CHECK"
$dataHit = $false
foreach ($f in $files) {
    $ext = [System.IO.Path]::GetExtension($f)
    if ($f -like 'data/*' -or $f -like 'evidence/*' -or
        $ext -in @('.duckdb', '.sqlite', '.sqlite3', '.db')) {
        Write-Fail "Evidence/data file present in repo: $f"
        $dataHit = $true
    }
}
if (-not $dataHit) { Write-OK "No evidence data files detected" }

# ─── 7. ORPHANED _DEPRECATED FILE CHECK ──────────────────────────────────────
Write-Section "7. ORPHANED _DEPRECATED CHECK"
$depFiles = (git ls-files -- '_DEPRECATED/' 2>$null) -split "`n" | Where-Object { $_ }
if ($depFiles.Count -gt 0) {
    Write-OK "$($depFiles.Count) file(s) in _DEPRECATED/ — verify they are listed in INDEX.md"
}

# ── SUMMARY ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "============================================"
Write-Host "Results: $FAIL fail(s), $WARNS warning(s)"
Write-Host "============================================"

if ($FAIL -gt 0) {
    Write-Host "GUARDRAIL CHECK FAILED — fix the issues above." -ForegroundColor Red
    exit 1
}
if ($WARNS -gt 0) {
    Write-Host "Guardrail check passed with warnings — review above." -ForegroundColor Yellow
    exit 0
}
Write-Host "All guardrail checks passed." -ForegroundColor Green
exit 0
