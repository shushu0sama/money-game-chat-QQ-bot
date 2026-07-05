from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from .graph_state import GraphState, ToolPlan
from .models import GraphDiagnostics


def create_run_id() -> str:
    return uuid4().hex


def ensure_run_id(state: GraphState) -> GraphState:
    if state.diagnostics.run_id:
        return state
    return replace(
        state,
        diagnostics=replace(state.diagnostics, run_id=create_run_id()),
    )


def record_node_visit(state: GraphState, node_name: str) -> GraphState:
    diagnostics = state.diagnostics
    return replace(
        state,
        diagnostics=replace(
            diagnostics,
            visited_nodes=diagnostics.visited_nodes + (node_name,),
        ),
    )


def record_decision(state: GraphState, decision: str) -> GraphState:
    diagnostics = state.diagnostics
    return replace(
        state,
        diagnostics=replace(
            diagnostics,
            decisions=diagnostics.decisions + (decision,),
        ),
    )


def summarize_tool_plan(tool_plan: ToolPlan) -> str:
    if tool_plan.tool_name is None:
        return f"no_tool:{tool_plan.rejection_reason or 'unmatched'}"
    confirmation = "confirm" if tool_plan.requires_confirmation else "no_confirm"
    return f"tool:{tool_plan.tool_name}:confidence={tool_plan.confidence:.2f}:{confirmation}"


def record_tool_plan(state: GraphState) -> GraphState:
    return record_decision(state, summarize_tool_plan(state.tool_plan))


def record_reply_policy(state: GraphState) -> GraphState:
    return record_decision(state, f"reply_policy:{state.reply_policy}")


def record_error(state: GraphState, error: Exception | str) -> GraphState:
    message = str(error)
    diagnostics = state.diagnostics
    return replace(
        state,
        diagnostics=GraphDiagnostics(
            run_id=diagnostics.run_id,
            visited_nodes=diagnostics.visited_nodes,
            decisions=diagnostics.decisions,
            error=message,
        ),
    )
