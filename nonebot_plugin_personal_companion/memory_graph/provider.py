from __future__ import annotations

from typing import Protocol

from ..state import GraphState, MemoryResult


class MemoryProvider(Protocol):
    def retrieve_memory(self, state: GraphState) -> MemoryResult: ...


class EmptyMemoryProvider:
    def retrieve_memory(self, state: GraphState) -> MemoryResult:
        return MemoryResult()


class StaticMemoryProvider:
    def __init__(self, memory: MemoryResult):
        self.memory = memory
        self.calls: list[GraphState] = []

    def retrieve_memory(self, state: GraphState) -> MemoryResult:
        self.calls.append(state)
        return self.memory
