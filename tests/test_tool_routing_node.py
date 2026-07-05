from nonebot_plugin_personal_companion.nodes import route_tool_node
from nonebot_plugin_personal_companion.state import GraphState, InboundMessage, IntentClassification
from nonebot_plugin_personal_companion.tools import ToolDescriptor, ToolRegistry


def make_registry(*descriptors):
    registry = ToolRegistry()
    for descriptor in descriptors:
        registry.register(descriptor)
    return registry


def test_route_tool_node_routes_reminder_request_to_fake_tool():
    registry = make_registry(ToolDescriptor(name="reminder", description="Create reminder", requires_confirmation=True))
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="明天提醒我交材料"),
        intent=IntentClassification(label="tool", confidence=0.8),
        reply_policy="tool_needed",
    )

    updated = route_tool_node(state, registry)

    assert updated.tool_plan.tool_name == "reminder"
    assert updated.tool_plan.arguments == {"text": "明天提醒我交材料"}
    assert updated.tool_plan.confidence == 0.8
    assert updated.tool_plan.requires_confirmation is True
    assert updated.diagnostics.visited_nodes == ("route_tool",)
    assert updated.diagnostics.decisions == ("tool_routed:reminder:confidence=0.80",)


def test_route_tool_node_routes_web_search_request_to_fake_tool():
    registry = make_registry(ToolDescriptor(name="web_search", description="Search web"))
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="查一下最近新闻"),
        intent=IntentClassification(label="tool", confidence=0.8),
        reply_policy="tool_needed",
    )

    updated = route_tool_node(state, registry)

    assert updated.tool_plan.tool_name == "web_search"
    assert updated.tool_plan.requires_confirmation is False


def test_route_tool_node_rejects_when_no_registered_tool_fits():
    registry = make_registry(ToolDescriptor(name="calendar", description="Calendar"))
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="帮我翻译这句话"),
        intent=IntentClassification(label="tool", confidence=0.8),
        reply_policy="tool_needed",
    )

    updated = route_tool_node(state, registry)

    assert updated.tool_plan.tool_name is None
    assert updated.tool_plan.rejection_reason == "no matching tool"
    assert updated.diagnostics.decisions == ("tool_rejected:no matching tool",)


def test_route_tool_node_rejects_when_policy_does_not_require_tool():
    registry = make_registry(ToolDescriptor(name="reminder", description="Create reminder"))
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="明天提醒我交材料"),
        intent=IntentClassification(label="chat", confidence=0.8),
        reply_policy="reply_now",
    )

    updated = route_tool_node(state, registry)

    assert updated.tool_plan.tool_name is None
    assert updated.tool_plan.rejection_reason == "reply policy does not require tool"


def test_route_tool_node_returns_new_state_and_does_not_mutate_original():
    registry = make_registry(ToolDescriptor(name="reminder", description="Create reminder"))
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="提醒我喝水"),
        intent=IntentClassification(label="tool", confidence=0.8),
        reply_policy="tool_needed",
    )

    updated = route_tool_node(state, registry)

    assert updated is not state
    assert state.tool_plan.tool_name is None
    assert state.diagnostics.visited_nodes == ()
