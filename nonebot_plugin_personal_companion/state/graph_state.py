from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from .models import GraphDiagnostics, InboundMessage

IntentLabel = Literal["unknown", "chat", "tool", "memory", "proactive"]
ReplyPolicy = Literal["undecided", "reply_now", "no_reply", "ask_clarification", "tool_needed"]


@dataclass(frozen=True)
class MemoryResult:
    recent_context: tuple[str, ...] = ()
    durable_facts: tuple[str, ...] = ()
    preferences: tuple[str, ...] = ()
    topic_candidates: tuple[str, ...] = ()


@dataclass(frozen=True)
class IntentClassification:
    label: IntentLabel = "unknown"
    confidence: float = 0.0
    reason: str | None = None


@dataclass(frozen=True)
class ToolPlan:
    tool_name: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    requires_confirmation: bool = False
    rejection_reason: str | None = None


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    success: bool
    content: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GeneratedResponse:
    text: str | None = None
    mode: ReplyPolicy = "undecided"


@dataclass(frozen=True)
class GraphState:
    inbound: InboundMessage
    recent_context: tuple[str, ...] = ()
    memory: MemoryResult = field(default_factory=MemoryResult)
    intent: IntentClassification = field(default_factory=IntentClassification)
    tool_plan: ToolPlan = field(default_factory=ToolPlan)
    reply_policy: ReplyPolicy = "undecided"
    generated_response: GeneratedResponse = field(default_factory=GeneratedResponse)
    tool_results: tuple[ToolResult, ...] = ()
    diagnostics: GraphDiagnostics = field(default_factory=GraphDiagnostics)
    proactive_trigger: dict[str, Any] | None = None


def initialize_graph_state(inbound: InboundMessage) -> GraphState:
    return GraphState(inbound=inbound)
