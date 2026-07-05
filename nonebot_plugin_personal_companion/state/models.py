from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

MessageSource = Literal["private", "group", "unknown"]


@dataclass(frozen=True)
class InboundMessage:
    user_id: str
    text: str
    source: MessageSource = "unknown"
    group_id: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphAction:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphDiagnostics:
    run_id: str | None = None
    visited_nodes: tuple[str, ...] = ()
    decisions: tuple[str, ...] = ()
    error: str | None = None


@dataclass(frozen=True)
class GraphOutput:
    should_reply: bool
    reply_text: str | None = None
    actions: tuple[GraphAction, ...] = ()
    diagnostics: GraphDiagnostics = field(default_factory=GraphDiagnostics)
