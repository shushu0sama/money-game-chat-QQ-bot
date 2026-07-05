from __future__ import annotations

from dataclasses import replace
from typing import Protocol

from ..state import GraphState, record_decision, record_node_visit


class RecentContextProvider(Protocol):
    def load_recent_context(self, user_id: str, limit: int = 8) -> tuple[str, ...]: ...


class EmptyRecentContextProvider:
    def load_recent_context(self, user_id: str, limit: int = 8) -> tuple[str, ...]:
        return ()


def load_context_node(
    state: GraphState,
    provider: RecentContextProvider | None = None,
    limit: int = 8,
) -> GraphState:
    provider = provider or EmptyRecentContextProvider()
    recent_context = provider.load_recent_context(state.inbound.user_id, limit=limit)
    updated = replace(state, recent_context=tuple(recent_context))
    updated = record_node_visit(updated, "load_context")
    return record_decision(updated, f"context_loaded:{len(updated.recent_context)}")
