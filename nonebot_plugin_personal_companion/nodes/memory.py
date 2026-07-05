from __future__ import annotations

from dataclasses import replace

from ..memory_graph import EmptyMemoryProvider, MemoryProvider
from ..state import GraphState, record_decision, record_node_visit


def retrieve_memory_node(
    state: GraphState,
    provider: MemoryProvider | None = None,
) -> GraphState:
    provider = provider or EmptyMemoryProvider()
    memory = provider.retrieve_memory(state)
    updated = replace(state, memory=memory)
    updated = record_node_visit(updated, "retrieve_memory")
    summary = (
        f"memory_loaded:recent={len(memory.recent_context)}:"
        f"facts={len(memory.durable_facts)}:"
        f"preferences={len(memory.preferences)}:"
        f"topics={len(memory.topic_candidates)}"
    )
    return record_decision(updated, summary)
