# =============================================================================
# MCP_PLATFORM pre-push hook — PowerShell
# Extends the existing secret scan with: stub check, DIAL ref check,
# CONDUCTOR GATE enforcement, and evidence data leak check
# Usage: Called by install-hooks.ps1 shim or directly via git hook
# =============================================================================
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$FAIL = 0

function Write-Fail { param([string]$msg) Write-Host "[FAIL] $msg" -ForegroundColor Red;  $script:FAIL++ }
function Write-OK   { param([string]$msg) Write-Host "[OK]   $msg" -ForegroundColor Green }
function Write-Warn { param([string]$msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow }

Write-Host "============================================"
Write-Host " MCP_PLATFORM pre-push guardrails"
Write-Host "============================================"

# Read stdin — git passes: <local-ref> SP <local-sha> SP <remote-ref> SP <remote-sha>
$input_lines = @($input)
if (-not $input_lines -or $input_lines.Count -eq 0) {
    # When run standalone, read from stdin pipe
    $input_lines = @([Console]::In.ReadToEnd() -split "`n" | Where-Object { $_ -ne '' })
}

if ($input_lines.Count -eq 0) {
    Write-OK "No push refs — nothing to check"
    exit 0
}

foreach ($line in $input_lines) {
    if (-not $line.Trim()) { continue }
    $parts = $line.Trim() -split '\s+'
    if ($parts.Count -lt 4) { continue }

    $localRef    = $parts[0]
    $localSha    = $parts[1]
    $remoteRef   = $parts[2]
    $remoteSha   = $parts[3]

    # Deleting branch
    if ($localSha -eq '0000000000000000000000000000000000000000') { continue }

    if ($remoteSha -eq '0000000000000000000000000000000000000000') {
        # New branch — check tip only
        $changed = (git diff-tree --no-commit-id -r --name-only $localSha 2>$null) -split "`n" | Where-Object { $_ }
    } else {
        $changed = (git diff --name-only "${remoteSha}..${localSha}" 2>$null) -split "`n" | Where-Object { $_ }
    }

    if (-not $changed) {
        Write-OK "No changed files in push range"
        continue
    }

    # ─── 1. SECRET SCAN ────────────────────────────────────────────────────────
    Write-Host ""
    Write-Host "[ 1/5 ] Secret scan..."

    $secretRules = @(
        @{ Pattern = 'gsk_[A-Za-z0-9]+';                                       Label = 'Groq API key' },
        @{ Pattern = 'sk-[A-Za-z0-9]{20,}';                                    Label = 'OpenAI-style API key' },
        @{ Pattern = 'AIza[0-9A-Za-z\-_]{35}';                                 Label = 'Google API key' },
        @{ Pattern = '-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----';   Label = 'Private key material' },
        @{ Pattern = 'CONDUCTOR_AUTH_SECRET\s*=\s*"[^"$]{8,}"';                Label = 'Hardcoded Conductor secret' }
    )
    $secretFound = $false
    foreach ($f in $changed) {
        if (-not $f) { continue }
        $content = git show "${localSha}:${f}" 2>$null
        if (-not $content) { continue }
        $lines = $content -split "`n"
        $lineNum = 0
        foreach ($ln in $lines) {
            $lineNum++
            foreach ($rule in $secretRules) {
                if ($ln -match $rule.Pattern) {
                    Write-Fail "Possible $($rule.Label) in ${f}:$lineNum"
                    $secretFound = $true
                }
            }
        }
    }
    if (-not $secretFound) { Write-OK "No secrets detected" }

    # ─── 2. STUB SCAN ──────────────────────────────────────────────────────────
    Write-Host ""
    Write-Host "[ 2/5 ] Stub scan..."

    $stubRegex   = 'TODO:|FIXME:|throw new Error\("not implemented"\)|NotImplementedError|raise NotImplementedError|pass\s*#\s*stub'
    $stubExts    = @('.ts', '.tsx', '.js', '.py')
    $stubExclude = @('_DEPRECATED/', 'docs/wiki/archive/')
    $stubFound   = $false

    foreach ($f in $changed) {
        $ext = [System.IO.Path]::GetExtension($f)
        if ($stubExts -notcontains $ext) { continue }
        $skip = $false
        foreach ($ex in $stubExclude) { if ($f -like "*$ex*") { $skip = $true; break } }
        if ($skip) { continue }
        $content = git show "${localSha}:${f}" 2>$null
        if (-not $content) { continue }
        $lines = $content -split "`n"
        $lineNum = 0
        foreach ($ln in $lines) {
            $lineNum++
            if ($ln -match $stubRegex) {
                Write-Fail "Stub in pushed file ${f}:$lineNum — $($ln.Trim())"
                $stubFound = $true
            }
        }
    }
    if (-not $stubFound) { Write-OK "No stubs detected" }

    # ─── 3. DIAL REFERENCE SCAN ────────────────────────────────────────────────
    Write-Host ""
    Write-Host "[ 3/5 ] DIAL reference scan (deprecated per ADR-033)..."

    $dialPattern = 'ai-dial-core|dial-chat|dial-stack|epam/ai-dial|aidial\.'
    $dialExts    = @('.ts', '.tsx', '.js', '.py', '.yml', '.yaml', '.json')
    $dialExclude = @('_DEPRECATED/', 'docs/wiki/archive/', 'DECISION_REGISTER')
    $dialFound   = $false

    foreach ($f in $changed) {
        $ext = [System.IO.Path]::GetExtension($f)
        if ($dialExts -notcontains $ext) { continue }
        $skip = $false
        foreach ($ex in $dialExclude) { if ($f -like "*$ex*") { $skip = $true; break } }
        if ($skip) { continue }
        $content = git show "${localSha}:${f}" 2>$null
        if (-not $content) { continue }
        $lines = $content -split "`n"
        $lineNum = 0
        foreach ($ln in $lines) {
            $lineNum++
            if ($ln -imatch $dialPattern) {
                Write-Fail "DIAL reference in active code ${f}:$lineNum — DIAL deprecated per ADR-033"
                $dialFound = $true
            }
        }
    }
    if (-not $dialFound) { Write-OK "No DIAL references in active code" }

    # ─── 4. EVIDENCE DATA LEAK CHECK ───────────────────────────────────────────
    Write-Host ""
    Write-Host "[ 4/5 ] Evidence data leak check..."

    $dataFound = $false
    foreach ($f in $changed) {
        $ext = [System.IO.Path]::GetExtension($f)
        if ($f -like 'data/*' -or $f -like 'evidence/*' -or
            $ext -in @('.duckdb', '.sqlite', '.sqlite3', '.db')) {
            Write-Fail "Evidence/data file in push: $f — never commit actual data"
            $dataFound = $true
        }
        if ($ext -eq '.ipynb') {
            $content = git show "${localSha}:${f}" 2>$null
            if ($content) {
                $outputCount = ([regex]::Matches($content, '"output_type"')).Count
                if ($outputCount -gt 0) {
                    Write-Warn "Notebook has $outputCount output cell(s): $f — strip outputs before pushing"
                }
            }
        }
    }
    if (-not $dataFound) { Write-OK "No evidence data files detected" }

    # ─── 5. CONDUCTOR GATE SUMMARY ─────────────────────────────────────────────
    Write-Host ""
    Write-Host "[ 5/5 ] Conductor gate check..."

    $gateFound = $false
    foreach ($f in $changed) {
        if ($f -match '(?:workflows|workflow-definitions)[/\\][^/\\]+\.json$') {
            $content = git show "${localSha}:${f}" 2>$null
            if ($content -and ($content -notmatch 'GATE-LIFTED')) {
                Write-Fail "Conductor workflow without GATE-LIFTED marker: $f"
                Write-Host "      CONDUCTOR GATE requires first end-to-end ingest test to pass." -ForegroundColor Yellow
                Write-Host "      Add '// GATE-LIFTED: <date> <approver>' to the workflow JSON." -ForegroundColor Yellow
                $gateFound = $true
            } else {
                Write-OK "GATE-LIFTED found in: $f"
            }
        }
    }
    if (-not $gateFound) { Write-OK "Conductor gate check passed" }
}

# ─── RESULT ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "============================================"
if ($FAIL -gt 0) {
    Write-Host "pre-push FAILED — push blocked. Fix issues above." -ForegroundColor Red
    exit 1
}
Write-Host "pre-push passed — safe to push." -ForegroundColor Green
exit 0
