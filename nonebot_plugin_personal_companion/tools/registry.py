from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

ToolExecutor = Callable[[dict[str, Any]], str]


@dataclass(frozen=True)
class ToolDescriptor:
    name: str
    description: str
    argument_schema: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False
    executor: ToolExecutor | None = None


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolDescriptor] = {}

    def register(self, descriptor: ToolDescriptor) -> None:
        if not descriptor.name.strip():
            raise ValueError("Tool name cannot be empty")
        self._tools[descriptor.name] = descriptor

    def get(self, name: str) -> ToolDescriptor | None:
        return self._tools.get(name)

    def list(self) -> tuple[ToolDescriptor, ...]:
        return tuple(self._tools.values())
