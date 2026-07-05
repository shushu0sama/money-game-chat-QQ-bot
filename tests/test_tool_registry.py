import pytest

from nonebot_plugin_personal_companion.state import ToolPlan
from nonebot_plugin_personal_companion.tools import ToolDescriptor, ToolRegistry


def test_tool_registry_registers_and_retrieves_descriptor():
    def executor(arguments):
        return f"created:{arguments['text']}"

    descriptor = ToolDescriptor(
        name="reminder",
        description="Create a reminder",
        argument_schema={"type": "object", "properties": {"text": {"type": "string"}}},
        requires_confirmation=True,
        executor=executor,
    )
    registry = ToolRegistry()

    registry.register(descriptor)

    found = registry.get("reminder")
    assert found == descriptor
    assert found is not None
    assert found.executor is executor
    assert found.requires_confirmation is True


def test_tool_registry_returns_none_for_missing_tool():
    registry = ToolRegistry()

    assert registry.get("missing") is None


def test_tool_registry_lists_registered_tools_in_order():
    registry = ToolRegistry()
    first = ToolDescriptor(name="search", description="Search web")
    second = ToolDescriptor(name="calendar", description="Create calendar event")

    registry.register(first)
    registry.register(second)

    assert registry.list() == (first, second)


def test_tool_registry_rejects_empty_tool_name():
    registry = ToolRegistry()

    with pytest.raises(ValueError, match="Tool name cannot be empty"):
        registry.register(ToolDescriptor(name=" ", description="Invalid"))


def test_tool_plan_supports_selection_and_rejection_fields():
    selected = ToolPlan(
        tool_name="reminder",
        arguments={"text": "交材料"},
        confidence=0.9,
        requires_confirmation=True,
    )
    rejected = ToolPlan(rejection_reason="no matching tool")

    assert selected.tool_name == "reminder"
    assert selected.arguments == {"text": "交材料"}
    assert selected.confidence == 0.9
    assert selected.requires_confirmation is True
    assert rejected.tool_name is None
    assert rejected.rejection_reason == "no matching tool"
