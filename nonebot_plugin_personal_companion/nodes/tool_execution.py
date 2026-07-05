from __future__ import annotations

from dataclasses import replace

from ..state import GraphState, ToolResult, record_decision, record_node_visit
from ..tools import ToolRegistry


def execute_tool_node(state: GraphState, registry: ToolRegistry, confirmed: bool = False) -> GraphState:
    updated = record_node_visit(state, "execute_tool")
    tool_plan = state.tool_plan

    if tool_plan.tool_name is None:
        result = ToolResult(tool_name="", success=False, error=tool_plan.rejection_reason or "no tool plan")
        updated = replace(updated, tool_results=updated.tool_results + (result,))
        return record_decision(updated, "tool_execution_skipped:no_tool_plan")

    descriptor = registry.get(tool_plan.tool_name)
    if descriptor is None:
        result = ToolResult(tool_name=tool_plan.tool_name, success=False, error="tool not registered")
        updated = replace(updated, tool_results=updated.tool_results + (result,))
        return record_decision(updated, f"tool_execution_failed:{tool_plan.tool_name}:not_registered")

    if tool_plan.requires_confirmation and not confirmed:
        result = ToolResult(tool_name=tool_plan.tool_name, success=False, error="confirmation required")
        updated = replace(updated, tool_results=updated.tool_results + (result,))
        return record_decision(updated, f"tool_execution_skipped:{tool_plan.tool_name}:confirmation_required")

    if descriptor.executor is None:
        result = ToolResult(tool_name=tool_plan.tool_name, success=False, error="executor missing")
        updated = replace(updated, tool_results=updated.tool_results + (result,))
        return record_decision(updated, f"tool_execution_failed:{tool_plan.tool_name}:executor_missing")

    try:
        content = descriptor.executor(tool_plan.arguments)
    except Exception as error:
        result = ToolResult(tool_name=tool_plan.tool_name, success=False, error=str(error))
        updated = replace(updated, tool_results=updated.tool_results + (result,))
        return record_decision(updated, f"tool_execution_failed:{tool_plan.tool_name}:exception")

    result = ToolResult(tool_name=tool_plan.tool_name, success=True, content=content)
    updated = replace(updated, tool_results=updated.tool_results + (result,))
    return record_decision(updated, f"tool_execution_succeeded:{tool_plan.tool_name}")
