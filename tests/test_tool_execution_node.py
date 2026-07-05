from nonebot_plugin_personal_companion.nodes import execute_tool_node
from nonebot_plugin_personal_companion.state import GraphState, InboundMessage, ToolPlan
from nonebot_plugin_personal_companion.tools import ToolDescriptor, ToolRegistry


def make_registry(*descriptors):
    registry = ToolRegistry()
    for descriptor in descriptors:
        registry.register(descriptor)
    return registry


def test_execute_tool_node_runs_fake_executor_successfully():
    calls = []

    def executor(arguments):
        calls.append(arguments)
        return f"created:{arguments['text']}"

    registry = make_registry(ToolDescriptor(name="reminder", description="Create reminder", executor=executor))
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="提醒我喝水"),
        tool_plan=ToolPlan(tool_name="reminder", arguments={"text": "提醒我喝水"}),
    )

    updated = execute_tool_node(state, registry)

    assert calls == [{"text": "提醒我喝水"}]
    assert updated.tool_results[0].tool_name == "reminder"
    assert updated.tool_results[0].success is True
    assert updated.tool_results[0].content == "created:提醒我喝水"
    assert updated.diagnostics.visited_nodes == ("execute_tool",)
    assert updated.diagnostics.decisions == ("tool_execution_succeeded:reminder",)


def test_execute_tool_node_skips_when_no_tool_plan_exists():
    registry = make_registry(ToolDescriptor(name="reminder", description="Create reminder"))
    state = GraphState(inbound=InboundMessage(user_id="10001", text="你好"))

    updated = execute_tool_node(state, registry)

    assert updated.tool_results[0].success is False
    assert updated.tool_results[0].error == "no tool plan"
    assert updated.diagnostics.decisions == ("tool_execution_skipped:no_tool_plan",)


def test_execute_tool_node_skips_confirmation_required_without_confirmation():
    registry = make_registry(ToolDescriptor(name="reminder", description="Create reminder", executor=lambda arguments: "ok"))
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="提醒我喝水"),
        tool_plan=ToolPlan(tool_name="reminder", arguments={"text": "提醒我喝水"}, requires_confirmation=True),
    )

    updated = execute_tool_node(state, registry, confirmed=False)

    assert updated.tool_results[0].success is False
    assert updated.tool_results[0].error == "confirmation required"
    assert updated.diagnostics.decisions == ("tool_execution_skipped:reminder:confirmation_required",)


def test_execute_tool_node_runs_confirmation_required_when_confirmed():
    registry = make_registry(ToolDescriptor(name="reminder", description="Create reminder", executor=lambda arguments: "ok"))
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="提醒我喝水"),
        tool_plan=ToolPlan(tool_name="reminder", arguments={"text": "提醒我喝水"}, requires_confirmation=True),
    )

    updated = execute_tool_node(state, registry, confirmed=True)

    assert updated.tool_results[0].success is True
    assert updated.tool_results[0].content == "ok"


def test_execute_tool_node_records_missing_registered_tool():
    registry = ToolRegistry()
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="提醒我喝水"),
        tool_plan=ToolPlan(tool_name="reminder", arguments={"text": "提醒我喝水"}),
    )

    updated = execute_tool_node(state, registry)

    assert updated.tool_results[0].success is False
    assert updated.tool_results[0].error == "tool not registered"
    assert updated.diagnostics.decisions == ("tool_execution_failed:reminder:not_registered",)


def test_execute_tool_node_records_executor_exception_without_raising():
    def executor(arguments):
        raise RuntimeError("boom")

    registry = make_registry(ToolDescriptor(name="reminder", description="Create reminder", executor=executor))
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="提醒我喝水"),
        tool_plan=ToolPlan(tool_name="reminder", arguments={"text": "提醒我喝水"}),
    )

    updated = execute_tool_node(state, registry)

    assert updated.tool_results[0].success is False
    assert updated.tool_results[0].error == "boom"
    assert updated.diagnostics.decisions == ("tool_execution_failed:reminder:exception",)


def test_execute_tool_node_returns_new_state_and_does_not_mutate_original():
    registry = make_registry(ToolDescriptor(name="reminder", description="Create reminder", executor=lambda arguments: "ok"))
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="提醒我喝水"),
        tool_plan=ToolPlan(tool_name="reminder", arguments={"text": "提醒我喝水"}),
    )

    updated = execute_tool_node(state, registry)

    assert updated is not state
    assert state.tool_results == ()
    assert state.diagnostics.visited_nodes == ()
