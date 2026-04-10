# Codex MCP Import Sources

Status: `partial`
Date: `2026-03-30`

This file records the user-level MCP sources reviewed while preparing the Codex import set in [`codex-mcp-import.toml`](/Users/matts/Projects/TheBigOne/dial-stack/docs/plans/codex-mcp-import.toml).

## Included

### `mem0`

- Source shape: user-provided MCP registry snippet
- Source shape: user-provided `mcpServers` snippet
- Normalized for Codex as:
  - `command = "uvx"`
  - `args = ["mem0-mcp-server"]`
- Notes:
  - `MEM0_DEFAULT_USER_ID` preserved as `matthew47`
  - `MEM0_API_KEY` moved to environment-based sourcing for a cleaner Codex config

### `mcp-structured-memory`

- Source shape: user-provided MCP registry snippet
- Source shape: user-provided `mcpServers` snippet
- Normalized for Codex as:
  - `command = "npx"`
  - `args = ["-y", "@nmeierpolys/mcp-structured-memory"]`

### `deepthinking`

- Source shape: user-provided MCP registry snippet
- Source shape: user-provided `mcpServers` snippet
- Normalized for Codex as:
  - `command = "npx"`
  - `args = ["deepthinking-mcp"]`
- Notes:
  - Windows path normalized to `C:\Users\matts\AI_Workspace\deepthinking-exports`

### `iventra-notebooklm-mcp`

- Source shape: user-provided MCP registry snippet
- Source shape: user-provided `mcpServers` snippet
- Normalized for Codex as:
  - `command = "npx"`
  - `args = ["-y", "notebooklm-mcp@latest"]`

### `mcp-sequentialthinking-tools`

- Source shape: user-provided MCP registry snippet
- Normalized for Codex as:
  - `command = "npx"`
  - `args = ["-y", "mcp-sequentialthinking-tools"]`

### `think-strategies`

- Source shape: user-provided MCP registry snippet
- Source shape: user-provided `mcpServers` snippet
- Normalized for Codex as disabled by default
- Reason:
  - user source already showed this as disabled in one source set

### `context7`

- Source shape: user-provided MCP registry snippet
- Normalized for Codex as:
  - remote MCP URL
  - `CONTEXT7_API_KEY` sourced from environment

### `verifiable-thinking`

- Source shape: user-provided MCP registry snippet
- Normalized for Codex as:
  - `command = "npx"`
  - `args = ["-y", "verifiable-thinking-mcp"]`

### `cachebro`

- Source shape:
  - [`C:\Users\matts\.claude\settings.json`](C:\Users\matts\.claude\settings.json)
  - [`C:\Users\matts\.claude\.claude.json`](C:\Users\matts\.claude\.claude.json)
  - [`C:\Users\matts\.gemini\antigravity\mcp_config.json`](C:\Users\matts\.gemini\antigravity\mcp_config.json)
- Normalized for Codex as:
  - `command = "npx"`
  - `args = ["cachebro", "serve"]`

### `gemini-mcp-tool`

- Source shape:
  - [`C:\Users\matts\.gemini\antigravity\mcp_config.json`](C:\Users\matts\.gemini\antigravity\mcp_config.json)
- Normalized for Codex as:
  - `command = "npx"`
  - `args = ["-y", "gemini-mcp-tool"]`
- Notes:
  - this is the cleanest Gemini bridge candidate found in the scanned user-level configs

### `claude-code-mcp`

- Source shape:
  - [`C:\Users\matts\.gemini\antigravity\mcp_config.json`](C:\Users\matts\.gemini\antigravity\mcp_config.json)
- Normalized for Codex as:
  - `command = "npx"`
  - `args = ["-y", "@steipete/claude-code-mcp@latest"]`
- Notes:
  - preferred over directly exposing `claude mcp serve`
  - this is a cleaner bridge package rather than a client-internal command surface

### `mcp-search`

- Source shape:
  - [`C:\Users\matts\.claude\plugins\marketplaces\thedotmack\plugin\.mcp.json`](C:\Users\matts\.claude\plugins\marketplaces\thedotmack\plugin\.mcp.json)
  - [`C:\Users\matts\.claude\plugins\marketplaces\thedotmack\plugin\scripts\mcp-server.cjs`](C:\Users\matts\.claude\plugins\marketplaces\thedotmack\plugin\scripts\mcp-server.cjs)
- Normalized for Codex as:
  - `command = "node"`
  - `args = ["C:\\Users\\matts\\.claude\\plugins\\marketplaces\\thedotmack\\plugin\\scripts\\mcp-server.cjs"]`
- Notes:
  - this turned out to be a real MCP server, not just Claude UI glue
  - tools exposed by the bundled script include memory search, timeline, batched observation fetch, and smart code structure search helpers
  - it may depend on the associated worker service being available

### `morph-mcp`

- Source shape: user-provided `mcpServers` snippet
- Existing Codex reference:
  - [`C:\Users\matts\.codex\config.toml`](C:\Users\matts\.codex\config.toml)
- Normalized for Codex as:
  - `command = "npx"`
  - `args = ["-y", "@morphllm/morphmcp"]`
- Notes:
  - removed `--api-key` from command args
  - API key sourced from environment instead
  - preserved `ENABLED_TOOLS = "edit_file,warpgrep_codebase_search"`

## Reviewed But Excluded

### `claude-code`

- Source shape: user-provided `mcpServers` snippet
- Excluded because:
  - this is a bridge back into Claude itself, not a neutral portable tool dependency

### OpenCode bridge MCP

- Reviewed surfaces:
  - [`C:\Users\matts\.opencode`](C:\Users\matts\.opencode)
  - [`C:\Users\matts\.config\opencode`](C:\Users\matts\.config\opencode)
  - [`C:\Users\matts\.local\share\opencode`](C:\Users\matts\.local\share\opencode)
- Result:
  - no equivalent ready-made OpenCode bridge MCP definition was found in the scanned paths
  - OpenCode assets found were mostly skills, commands, agents, package scaffolding, and local runtime state
  - best next step for OpenCode is likely a dedicated bridge MCP or a Codex skill describing OpenCode API/A2A usage patterns rather than a direct config transplant

## Additional Source Surfaces Reviewed

### Claude

- [`C:\Users\matts\.claude\settings.json`](C:\Users\matts\.claude\settings.json)
- [`C:\Users\matts\.claude\.claude.json`](C:\Users\matts\.claude\.claude.json)
- [`C:\Users\matts\.claude\my-plugins`](C:\Users\matts\.claude\my-plugins)

Findings:

- explicit user-level MCP registration found for `cachebro`
- large plugin cache exists with many `.mcp.json` files, but those are not the same as a clean user-selected Codex import list
- `mcp-search` from the `thedotmack` plugin was upgraded from tentative to included after confirming it exposes a real standalone MCP server via `.mcp.json` and `scripts/mcp-server.cjs`
- `my-plugins` appears to be custom Claude plugin content, but this pass still focused on portable MCP server definitions first

### OpenCode

- [`C:\Users\matts\.config\opencode`](C:\Users\matts\.config\opencode)
- [`C:\Users\matts\.local\share\opencode`](C:\Users\matts\.local\share\opencode)
- [`C:\Users\matts\.local\share\opencode\MCP_DOCUMENTATION.md`](C:\Users\matts\.local\share\opencode\MCP_DOCUMENTATION.md)

Findings:

- OpenCode documentation says MCP config should live at `~/.local/share/opencode/mcp.json`
- that file was not present at scan time
- OpenCode still provided useful source evidence about intended MCP portability and layout

### Gemini

- [`C:\Users\matts\.gemini\settings.json`](C:\Users\matts\.gemini\settings.json)
- [`C:\Users\matts\.gemini\antigravity\mcp_config.json`](C:\Users\matts\.gemini\antigravity\mcp_config.json)

Findings:

- Gemini had the richest bridge-oriented MCP registry among the scanned user-level configs
- it already included:
  - `gemini-mcp-tool`
  - `claude-code-mcp`
  - `mcp-structured-memory`
  - `mem0`
  - `context7`
  - `cachebro`
- this made Gemini config a strong source of truth for portable Codex MCP carryover

## Import Guidance

To merge this into Codex manually:

1. Copy the relevant `[mcp_servers.*]` blocks from [`codex-mcp-import.toml`](C:\Users\matts\Projects\TheBigOne\dial-stack\docs\plans\codex-mcp-import.toml) into [`C:\Users\matts\.codex\config.toml`](C:\Users\matts\.codex\config.toml).
2. Ensure these environment variables exist before launch:
   - `MEM0_API_KEY`
   - `CONTEXT7_API_KEY`
   - `MORPH_API_KEY`
3. Verify bridge servers after adding them:
   - `mcp-search` may need its worker service reachable
   - `claude-code-mcp` depends on the bridge package rather than Claude internals
   - `gemini-mcp-tool` depends on the package being resolvable in your environment
4. Leave `think-strategies` disabled until you decide you want it active.

## Status Labels

- `implemented`: import-ready TOML created
- `partial`: not yet merged into live Codex config
- `historical`: Claude/OpenCode source registries and plugin caches
