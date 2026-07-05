from datetime import datetime
from zoneinfo import ZoneInfo

from nonebot_plugin_personal_companion.nodes import execute_tool_node, route_tool_node
from nonebot_plugin_personal_companion.reminders import parse_reminder
from nonebot_plugin_personal_companion.state import GraphState, InboundMessage, IntentClassification
from nonebot_plugin_personal_companion.tools import ToolRegistry, build_reminder_tool, execute_reminder_tool


class FakeReminderService:
    def __init__(self):
        self.created = []

    def try_parse(self, user_msg: str):
        return parse_reminder(
            user_msg,
            now=datetime(2026, 6, 28, 12, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
            timezone_name="Asia/Shanghai",
        )

    def create_from_parse(self, user_id: int, parsed) -> int:
        self.created.append((user_id, parsed))
        return len(self.created)


def test_execute_reminder_tool_creates_reminder_from_existing_parser():
    service = FakeReminderService()

    reply = execute_reminder_tool(service, "10001", {"text": "明天下午3点提醒我交材料"})

    assert reply == "好呀，我会在明天 15:00提醒你：交材料"
    assert len(service.created) == 1
    assert service.created[0][0] == 10001
    assert service.created[0][1].content == "交材料"


def test_execute_reminder_tool_returns_clarification_for_incomplete_request():
    service = FakeReminderService()

    reply = execute_reminder_tool(service, "10001", {"text": "明天下午提醒我交材料"})

    assert "几点提醒你交材料" in reply
    assert service.created == []


def test_reminder_tool_descriptor_executes_with_user_id():
    service = FakeReminderService()
    descriptor = build_reminder_tool(service, "10001")

    reply = descriptor.executor({"text": "明天下午3点提醒我交材料"})

    assert descriptor.name == "reminder"
    assert descriptor.requires_confirmation is False
    assert reply == "好呀，我会在明天 15:00提醒你：交材料"
    assert service.created[0][0] == 10001


def test_reminder_tool_runs_end_to_end_through_routing_and_execution_nodes():
    service = FakeReminderService()
    registry = ToolRegistry()
    registry.register(build_reminder_tool(service, "10001"))
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="明天下午3点提醒我交材料"),
        intent=IntentClassification(label="tool", confidence=0.8),
        reply_policy="tool_needed",
    )

    routed = route_tool_node(state, registry)
    executed = execute_tool_node(routed, registry)

    assert routed.tool_plan.tool_name == "reminder"
    assert executed.tool_results[0].success is True
    assert executed.tool_results[0].content == "好呀，我会在明天 15:00提醒你：交材料"
    assert len(service.created) == 1
    assert executed.diagnostics.visited_nodes == ("route_tool", "execute_tool")
    assert executed.diagnostics.decisions == (
        "tool_routed:reminder:confidence=0.80",
        "tool_execution_succeeded:reminder",
    )
