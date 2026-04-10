"""
Config-Driven Workflow Engine — Composite tools that run modules from config.

Workflows are defined in config/workflows.json and can be:
- Added/removed/reordered by editing the config
- Enabled/disabled without code changes
- Modified at runtime via workflow_update_config tool
- Extended with new modules by adding them to the modules section

Everything is configurable. Nothing is hardcoded.
"""

import json
import logging
import os
import time
from typing import Optional

from .audit_hooks import audit_tool

logger = logging.getLogger("dial-py-mcp-workflows")

# ---------------------------------------------------------------------------
# Config Loading
# ---------------------------------------------------------------------------

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "config",
    "workflows.json",
)

_workflow_config = None


def _load_config():
    """Load workflow configuration from JSON file."""
    global _workflow_config
    if _workflow_config is None:
        try:
            with open(CONFIG_PATH, "r") as f:
                _workflow_config = json.load(f)
            logger.info(f"[Workflows] Loaded config from {CONFIG_PATH}")
        except Exception as e:
            logger.error(f"[Workflows] Failed to load config: {e}")
            _workflow_config = {"modules": {}, "workflows": {}}
    return _workflow_config


def _reload_config():
    """Force reload of workflow configuration (for runtime updates)."""
    global _workflow_config
    _workflow_config = None
    return _load_config()


# ---------------------------------------------------------------------------
# Tool Registry (maps tool names to actual functions)
# ---------------------------------------------------------------------------

_tool_registry = {}


def register_tool(name: str, func):
    """Register a tool function by name for workflow execution."""
    _tool_registry[name] = func
    logger.info(f"[Workflows] Registered tool: {name}")


def _get_tool_func(tool_name: str):
    """Get a tool function by name from the registry."""
    return _tool_registry.get(tool_name)


# ---------------------------------------------------------------------------
# MCP Tools: Workflow Management
# ---------------------------------------------------------------------------


@audit_tool("workflow_list")
def workflow_list() -> str:
    """
    List all available workflows and their modules.

    Returns:
        JSON with workflows, their modules, and enabled status.
    """
    config = _load_config()

    result = {"workflows": {}, "modules": {}}

    for wf_id, wf in config.get("workflows", {}).items():
        result["workflows"][wf_id] = {
            "name": wf.get("name", wf_id),
            "description": wf.get("description", ""),
            "modules": wf.get("modules", []),
            "enabled": wf.get("enabled", True),
        }

    for mod_id, mod in config.get("modules", {}).items():
        result["modules"][mod_id] = {
            "name": mod.get("name", mod_id),
            "tool": mod.get("tool", ""),
            "enabled": mod.get("enabled", True),
        }

    return json.dumps(result, indent=2)


@audit_tool("workflow_run")
def workflow_run(
    text: str, workflow_name: str = "full_analysis", mode: str = "pass1"
) -> str:
    """
    Run a configured workflow on text.

    Executes modules in the order defined in config/workflows.json.
    Each module's output is passed as context to the next module.
    Disabled modules are skipped. Missing tools are logged but don't stop the workflow.

    Args:
        text: Text to analyze
        workflow_name: Name of workflow from config (default: full_analysis)
        mode: "pass1" (blind) or "pass2" (hindsight) — passed to modules that support it

    Returns:
        JSON with:
        - workflow: str — workflow name
        - results: dict — {module_id: tool_output}
        - skipped: list[str] — disabled or missing modules
        - metadata: {total_time_ms, module_count}
    """
    start = time.time()
    config = _load_config()

    workflow = config.get("workflows", {}).get(workflow_name)
    if not workflow:
        return json.dumps({"error": f"Workflow '{workflow_name}' not found"})

    if not workflow.get("enabled", True):
        return json.dumps({"error": f"Workflow '{workflow_name}' is disabled"})

    results = {}
    skipped = []
    current_text = text
    context = ""

    for module_id in workflow.get("modules", []):
        module = config.get("modules", {}).get(module_id)
        if not module:
            skipped.append(f"{module_id} (not in config)")
            continue

        if not module.get("enabled", True):
            skipped.append(f"{module_id} (disabled)")
            continue

        tool_name = module.get("tool", "")
        tool_func = _get_tool_func(tool_name)

        if not tool_func:
            skipped.append(f"{module_id} (tool '{tool_name}' not registered)")
            continue

        try:
            mod_start = time.time()
            module_config = module.get("config", {})

            # Call tool with appropriate arguments
            if tool_name.startswith("dpk_"):
                if tool_name == "dpk_hap_score":
                    result = tool_func(
                        current_text, mode=module_config.get("mode", mode)
                    )
                elif tool_name == "dpk_pii_redact":
                    result = tool_func(
                        current_text, operator=module_config.get("operator", "replace")
                    )
                else:
                    result = tool_func(current_text)
            elif tool_name.startswith("user_"):
                result = tool_func(current_text, context=context, mode=mode)
            elif tool_name == "fingerprint_voice":
                result = tool_func(current_text)
            elif tool_name == "semantica_extract_entities":
                result = tool_func(current_text)
            else:
                # Generic call
                result = tool_func(current_text)

            mod_time = int((time.time() - mod_start) * 1000)

            results[module_id] = {
                "output": json.loads(result) if isinstance(result, str) else result,
                "time_ms": mod_time,
            }

            # Build context for next module
            context += f"\n[{module_id}]: {result[:500]}"

        except Exception as e:
            logger.error(f"[Workflows] Module {module_id} failed: {e}")
            results[module_id] = {"error": str(e)}

    total_time = int((time.time() - start) * 1000)

    return json.dumps(
        {
            "workflow": workflow_name,
            "results": results,
            "skipped": skipped,
            "metadata": {
                "total_time_ms": total_time,
                "module_count": len(results),
                "skipped_count": len(skipped),
            },
        },
        indent=2,
    )


@audit_tool("workflow_update_config")
def workflow_update_config(config_json: str) -> str:
    """
    Update workflow configuration at runtime.

    Allows adding/removing/enabling/disabling modules and workflows
    without restarting the server.

    Args:
        config_json: JSON object with partial config updates.
                     Can include "modules" and/or "workflows" sections.

    Returns:
        JSON with updated config summary.
    """
    global _workflow_config

    try:
        updates = json.loads(config_json)
        config = _load_config()

        # Merge module updates
        if "modules" in updates:
            for mod_id, mod_data in updates["modules"].items():
                if mod_id in config["modules"]:
                    config["modules"][mod_id].update(mod_data)
                else:
                    config["modules"][mod_id] = mod_data

        # Merge workflow updates
        if "workflows" in updates:
            for wf_id, wf_data in updates["workflows"].items():
                if wf_id in config["workflows"]:
                    config["workflows"][wf_id].update(wf_data)
                else:
                    config["workflows"][wf_id] = wf_data

        # Save updated config
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)

        # Reload
        _reload_config()

        return json.dumps(
            {
                "success": True,
                "message": "Workflow config updated",
                "workflows": list(config.get("workflows", {}).keys()),
                "modules": list(config.get("modules", {}).keys()),
            }
        )

    except Exception as e:
        logger.error(f"[Workflows] Config update failed: {e}")
        return json.dumps({"error": str(e)})


@audit_tool("workflow_add_module")
def workflow_add_module(
    workflow_name: str, module_id: str, position: Optional[int] = None
) -> str:
    """
    Add a module to a workflow at runtime.

    Args:
        workflow_name: Name of workflow to modify
        module_id: ID of module to add (must exist in modules section)
        position: Optional position to insert at (0-indexed). Appends if not specified.

    Returns:
        JSON with updated workflow.
    """
    global _workflow_config
    config = _load_config()

    workflow = config.get("workflows", {}).get(workflow_name)
    if not workflow:
        return json.dumps({"error": f"Workflow '{workflow_name}' not found"})

    if module_id not in config.get("modules", {}):
        return json.dumps({"error": f"Module '{module_id}' not found in modules"})

    modules = workflow.get("modules", [])
    if module_id in modules:
        return json.dumps({"error": f"Module '{module_id}' already in workflow"})

    if position is not None:
        modules.insert(position, module_id)
    else:
        modules.append(module_id)

    workflow["modules"] = modules

    # Save and reload
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    _reload_config()

    return json.dumps(
        {
            "success": True,
            "workflow": workflow_name,
            "modules": modules,
        }
    )


@audit_tool("workflow_remove_module")
def workflow_remove_module(workflow_name: str, module_id: str) -> str:
    """
    Remove a module from a workflow at runtime.

    Args:
        workflow_name: Name of workflow to modify
        module_id: ID of module to remove

    Returns:
        JSON with updated workflow.
    """
    global _workflow_config
    config = _load_config()

    workflow = config.get("workflows", {}).get(workflow_name)
    if not workflow:
        return json.dumps({"error": f"Workflow '{workflow_name}' not found"})

    modules = workflow.get("modules", [])
    if module_id not in modules:
        return json.dumps({"error": f"Module '{module_id}' not in workflow"})

    modules.remove(module_id)
    workflow["modules"] = modules

    # Save and reload
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    _reload_config()

    return json.dumps(
        {
            "success": True,
            "workflow": workflow_name,
            "modules": modules,
        }
    )
