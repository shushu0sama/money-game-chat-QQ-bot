from __future__ import annotations

from langgraph.graph import END, StateGraph

from ..nodes import (
    RecentContextProvider,
    ResponseLLMClient,
    decide_reply_node,
    generate_response_node,
    load_context_node,
    normalize_input_node,
)
from ..state import GraphOutput, GraphState, InboundMessage, ensure_run_id, initialize_graph_state, record_reply_policy


def build_message_graph(
    llm_client: ResponseLLMClient,
    context_provider: RecentContextProvider | None = None,
):
    graph = StateGraph(GraphState)

    graph.add_node("ensure_run_id", ensure_run_id)
    graph.add_node("normalize_input", normalize_input_node)
    graph.add_node("load_context", lambda state: load_context_node(state, provider=context_provider))
    graph.add_node("decide_reply", decide_reply_node)
    graph.add_node("record_reply_policy", record_reply_policy)
    graph.add_node("generate_response", lambda state: generate_response_node(state, llm_client))

    graph.set_entry_point("ensure_run_id")
    graph.add_edge("ensure_run_id", "normalize_input")
    graph.add_edge("normalize_input", "load_context")
    graph.add_edge("load_context", "decide_reply")
    graph.add_edge("decide_reply", "record_reply_policy")
    graph.add_edge("record_reply_policy", "generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile()


def invoke_message_graph(
    inbound: InboundMessage,
    llm_client: ResponseLLMClient,
    context_provider: RecentContextProvider | None = None,
) -> GraphOutput:
    graph = build_message_graph(llm_client=llm_client, context_provider=context_provider)
    final_state = graph.invoke(initialize_graph_state(inbound))
    if isinstance(final_state, dict):
        final_state = GraphState(**final_state)
    return finalize_message_output(final_state)


def finalize_message_output(state: GraphState) -> GraphOutput:
    reply_text = state.generated_response.text
    should_reply = state.reply_policy != "no_reply" and bool(reply_text)
    return GraphOutput(
        should_reply=should_reply,
        reply_text=reply_text if should_reply else None,
        diagnostics=state.diagnostics,
    )
