from __future__ import annotations

from dataclasses import replace

from langgraph.graph import END, StateGraph

from ..state import (
    ProactiveOutput,
    ProactiveState,
    ProactiveTrigger,
    initialize_proactive_state,
)
from ..state.diagnostics import ensure_run_id, record_decision, record_node_visit


def normalize_proactive_trigger_node(state: ProactiveState) -> ProactiveState:
    trigger = ProactiveTrigger(
        reason=state.trigger.reason.strip(),
        target_user_id=str(state.trigger.target_user_id).strip(),
        current_time=state.trigger.current_time,
        metadata=dict(state.trigger.metadata),
    )
    updated = replace(state, trigger=trigger)
    return _record_proactive_node(updated, "normalize_proactive_trigger")


def load_proactive_context_node(state: ProactiveState) -> ProactiveState:
    updated = _record_proactive_node(state, "load_proactive_context")
    return _record_proactive_decision(updated, f"proactive_context_loaded:{len(updated.user_context)}")


def decide_proactive_action_node(state: ProactiveState) -> ProactiveState:
    updated = replace(state, candidate_action="none", final_decision="none", message_text=None)
    updated = _record_proactive_node(updated, "decide_proactive_action")
    return _record_proactive_decision(updated, "proactive_decision:none")


def finalize_proactive_output(state: ProactiveState) -> ProactiveOutput:
    should_send = state.final_decision == "send_message" and bool(state.message_text)
    return ProactiveOutput(
        action_type=state.final_decision,
        should_send=should_send,
        message_text=state.message_text if should_send else None,
        diagnostics=state.diagnostics,
    )


def build_proactive_graph():
    graph = StateGraph(ProactiveState)
    graph.add_node("ensure_run_id", _ensure_proactive_run_id)
    graph.add_node("normalize_trigger", normalize_proactive_trigger_node)
    graph.add_node("load_context", load_proactive_context_node)
    graph.add_node("decide_action", decide_proactive_action_node)

    graph.set_entry_point("ensure_run_id")
    graph.add_edge("ensure_run_id", "normalize_trigger")
    graph.add_edge("normalize_trigger", "load_context")
    graph.add_edge("load_context", "decide_action")
    graph.add_edge("decide_action", END)
    return graph.compile()


def invoke_proactive_graph(trigger: ProactiveTrigger) -> ProactiveOutput:
    graph = build_proactive_graph()
    final_state = graph.invoke(initialize_proactive_state(trigger))
    if isinstance(final_state, dict):
        final_state = ProactiveState(**final_state)
    return finalize_proactive_output(final_state)


def _ensure_proactive_run_id(state: ProactiveState) -> ProactiveState:
    graph_state = _as_graph_state_proxy(state)
    updated = ensure_run_id(graph_state)
    return replace(state, diagnostics=updated.diagnostics)


def _record_proactive_node(state: ProactiveState, node_name: str) -> ProactiveState:
    graph_state = _as_graph_state_proxy(state)
    updated = record_node_visit(graph_state, node_name)
    return replace(state, diagnostics=updated.diagnostics)


def _record_proactive_decision(state: ProactiveState, decision: str) -> ProactiveState:
    graph_state = _as_graph_state_proxy(state)
    updated = record_decision(graph_state, decision)
    return replace(state, diagnostics=updated.diagnostics)


def _as_graph_state_proxy(state: ProactiveState):
    from ..state import GraphState, InboundMessage

    return GraphState(
        inbound=InboundMessage(user_id=state.trigger.target_user_id, text="", metadata=state.trigger.metadata),
        diagnostics=state.diagnostics,
    )
