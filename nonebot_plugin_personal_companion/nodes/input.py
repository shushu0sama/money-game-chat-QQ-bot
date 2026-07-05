from __future__ import annotations

from dataclasses import replace

from ..state import GraphState, InboundMessage, record_node_visit


def normalize_input_node(state: GraphState) -> GraphState:
    inbound = state.inbound
    normalized = InboundMessage(
        user_id=str(inbound.user_id).strip(),
        group_id=str(inbound.group_id).strip() if inbound.group_id is not None else None,
        source=inbound.source,
        text=inbound.text.strip(),
        timestamp=inbound.timestamp,
        metadata=dict(inbound.metadata),
    )
    return record_node_visit(replace(state, inbound=normalized), "normalize_input")
