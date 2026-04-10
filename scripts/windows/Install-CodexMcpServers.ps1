param(
    [switch]$IncludeOptional
)

$ErrorActionPreference = "Stop"

function Write-Section {
    param([string]$Message)
    Write-Host ""
    Write-Host "== $Message ==" -ForegroundColor Cyan
}

function Resolve-CommandPath {
    param([string]$Name)
    $matches = & cmd.exe /c "where $Name" 2>$null
    if (-not $matches) {
        return $null
    }

    return ($matches | Select-Object -First 1).Trim()
}

function Resolve-PreferredPath {
    param(
        [string[]]$Candidates
    )

    foreach ($candidate in $Candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }

    return $null
}

function Get-CommandInfo {
    param(
        [string]$Label,
        [string]$Path
    )

    $version = $null
    if ($Path) {
        try {
            $version = & $Path --version 2>$null | Select-Object -First 1
        } catch {
        }
    }

    [pscustomobject]@{
        Name    = $Label
        Source  = $Path
        Version = $version
    }
}

function Install-NpmGlobalPackage {
    param(
        [string]$NpmCommand,
        [string]$Package
    )

    Write-Host "Installing npm package globally: $Package"
    & $NpmCommand install -g $Package
}

function Install-UvTool {
    param(
        [string]$UvCommand,
        [string]$Package
    )

    Write-Host "Installing uv tool globally: $Package"
    & $UvCommand tool install $Package
}

$nodePath = Resolve-PreferredPath -Candidates @(
    (Resolve-CommandPath -Name "node.exe"),
    "C:\Program Files\nodejs\node.exe"
)
$npmPath = Resolve-PreferredPath -Candidates @(
    (Resolve-CommandPath -Name "npm.cmd"),
    "C:\Program Files\nodejs\npm.cmd"
)
$npxPath = Resolve-PreferredPath -Candidates @(
    (Resolve-CommandPath -Name "npx.cmd"),
    "C:\Program Files\nodejs\npx.cmd"
)
$uvPath = Resolve-PreferredPath -Candidates @(
    (Resolve-CommandPath -Name "uv.exe"),
    "C:\Users\matts\AppData\Local\Microsoft\WinGet\Links\uv.exe"
)

$commandResults = @(
    Get-CommandInfo -Label "node" -Path $nodePath
    Get-CommandInfo -Label "npm" -Path $npmPath
    Get-CommandInfo -Label "npx" -Path $npxPath
    Get-CommandInfo -Label "uv" -Path $uvPath
)

Write-Section "Detected Windows toolchain"
$commandResults | Format-Table -AutoSize

if (-not $nodePath -or -not $npmPath -or -not $npxPath) {
    throw "Missing required Windows Node.js commands. Install Node.js LTS first, then rerun this script."
}

if (-not $uvPath) {
    throw "uv.exe is not on the Windows PATH yet. Restart Codex or open a new terminal after the install, then rerun this script."
}

$npmPackages = @(
    "gemini-mcp-tool",
    "@steipete/claude-code-mcp@latest",
    "mcp-sequentialthinking-tools",
    "@nmeierpolys/mcp-structured-memory",
    "@morphllm/morphmcp"
)

$uvTools = @(
    "mem0-mcp-server"
)

if ($IncludeOptional) {
    $npmPackages += @(
        "cachebro",
        "notebooklm-mcp@latest"
    )
}

Write-Section "Installing enabled npm-based MCP servers"
foreach ($package in $npmPackages) {
    Install-NpmGlobalPackage -NpmCommand $npmPath -Package $package
}

Write-Section "Installing enabled uv-based MCP servers"
foreach ($package in $uvTools) {
    Install-UvTool -UvCommand $uvPath -Package $package
}

Write-Section "Done"
Write-Host "Installed enabled Codex MCP dependencies globally on Windows."
Write-Host "Optional disabled MCPs are skipped by default."
