from __future__ import annotations

from typing import Any, Protocol

from .registry import ToolDescriptor


class ReminderServiceLike(Protocol):
    def try_parse(self, user_msg: str): ...
    def create_from_parse(self, user_id: int, parsed) -> int: ...


def build_reminder_tool(reminder_service: ReminderServiceLike, user_id: str) -> ToolDescriptor:
    return ToolDescriptor(
        name="reminder",
        description="Create a local reminder from a natural language reminder request.",
        argument_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
            },
            "required": ["text"],
        },
        requires_confirmation=False,
        executor=lambda arguments: execute_reminder_tool(reminder_service, user_id, arguments),
    )


def execute_reminder_tool(reminder_service: ReminderServiceLike, user_id: str, arguments: dict[str, Any]) -> str:
    text = str(arguments.get("text", "")).strip()
    if not text:
        return "你想让我提醒你什么？"

    parsed = reminder_service.try_parse(text)
    if parsed is None:
        return "这句话不像提醒请求。你可以说「明天下午3点提醒我开会」。"
    if not parsed.ok:
        return parsed.clarification

    reminder_service.create_from_parse(int(user_id), parsed)
    return parsed.confirmation
