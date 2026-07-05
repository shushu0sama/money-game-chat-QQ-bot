from __future__ import annotations

from dataclasses import replace

from ..state import GraphState, ToolPlan, record_decision, record_node_visit
from ..tools import ToolRegistry

_TOOL_KEYWORDS: dict[str, tuple[str, ...]] = {
    "reminder": ("提醒", "提醒我", "定时"),
    "calendar": ("日历", "会议", "日程"),
    "web_search": ("搜索", "查一下", "搜一下", "最新", "最近"),
}


def route_tool_node(state: GraphState, registry: ToolRegistry) -> GraphState:
    tool_plan = _route_tool(state, registry)
    updated = replace(state, tool_plan=tool_plan)
    updated = record_node_visit(updated, "route_tool")
    if tool_plan.tool_name:
        decision = f"tool_routed:{tool_plan.tool_name}:confidence={tool_plan.confidence:.2f}"
    else:
        decision = f"tool_rejected:{tool_plan.rejection_reason or 'no matching tool'}"
    return record_decision(updated, decision)


def _route_tool(state: GraphState, registry: ToolRegistry) -> ToolPlan:
    text = state.inbound.text
    if state.reply_policy != "tool_needed" and state.intent.label != "tool":
        return ToolPlan(rejection_reason="reply policy does not require tool")

    for descriptor in registry.list():
        keywords = _TOOL_KEYWORDS.get(descriptor.name, (descriptor.name,))
        if any(keyword in text for keyword in keywords):
            return ToolPlan(
                tool_name=descriptor.name,
                arguments={"text": text},
                confidence=0.8,
                requires_confirmation=descriptor.requires_confirmation,
            )

    return ToolPlan(rejection_reason="no matching tool")
