from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

from .models import GraphDiagnostics

ProactiveActionType = Literal["none", "send_message", "create_reminder", "log_only"]


@dataclass(frozen=True)
class ProactiveTrigger:
    reason: str
    target_user_id: str
    current_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProactiveState:
    trigger: ProactiveTrigger
    user_context: tuple[str, ...] = ()
    recent_interaction_state: dict[str, Any] = field(default_factory=dict)
    candidate_action: ProactiveActionType = "none"
    final_decision: ProactiveActionType = "none"
    message_text: str | None = None
    diagnostics: GraphDiagnostics = field(default_factory=GraphDiagnostics)


@dataclass(frozen=True)
class ProactiveOutput:
    action_type: ProactiveActionType = "none"
    should_send: bool = False
    message_text: str | None = None
    diagnostics: GraphDiagnostics = field(default_factory=GraphDiagnostics)


def initialize_proactive_state(trigger: ProactiveTrigger) -> ProactiveState:
    return ProactiveState(trigger=trigger)
