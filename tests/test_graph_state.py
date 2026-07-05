from nonebot_plugin_personal_companion.state import (
    GeneratedResponse,
    GraphState,
    InboundMessage,
    IntentClassification,
    MemoryResult,
    ToolPlan,
    ToolResult,
    initialize_graph_state,
)


def test_initialize_graph_state_from_inbound_message():
    inbound = InboundMessage(user_id="10001", text="你好", source="private")

    state = initialize_graph_state(inbound)

    assert state.inbound == inbound
    assert state.recent_context == ()
    assert state.memory == MemoryResult()
    assert state.intent == IntentClassification()
    assert state.tool_plan == ToolPlan()
    assert state.reply_policy == "undecided"
    assert state.generated_response == GeneratedResponse()
    assert state.tool_results == ()
    assert state.proactive_trigger is None


def test_graph_state_contains_message_and_future_proactive_fields():
    inbound = InboundMessage(user_id="10001", text="定时提醒我喝水", source="private")
    state = GraphState(
        inbound=inbound,
        proactive_trigger={"reason": "scheduled_check"},
    )

    assert state.inbound.text == "定时提醒我喝水"
    assert state.proactive_trigger == {"reason": "scheduled_check"}


def test_graph_state_accepts_structured_memory_intent_tool_and_results():
    inbound = InboundMessage(user_id="10001", text="明天提醒我交材料", source="private")
    state = GraphState(
        inbound=inbound,
        recent_context=("昨天聊过申请材料",),
        memory=MemoryResult(
            recent_context=("昨天聊过申请材料",),
            durable_facts=("用户正在准备申请材料",),
            preferences=("用户喜欢简短提醒",),
            topic_candidates=("申请材料",),
        ),
        intent=IntentClassification(label="tool", confidence=0.9, reason="包含提醒请求"),
        tool_plan=ToolPlan(
            tool_name="reminder",
            arguments={"text": "交材料"},
            confidence=0.9,
            requires_confirmation=True,
        ),
        reply_policy="tool_needed",
        generated_response=GeneratedResponse(text="要我明天几点提醒你？", mode="ask_clarification"),
        tool_results=(ToolResult(tool_name="reminder", success=False, error="missing time"),),
    )

    assert state.memory.durable_facts == ("用户正在准备申请材料",)
    assert state.intent.label == "tool"
    assert state.tool_plan.tool_name == "reminder"
    assert state.reply_policy == "tool_needed"
    assert state.generated_response.text == "要我明天几点提醒你？"
    assert state.tool_results[0].error == "missing time"


def test_graph_state_is_nonebot_independent():
    inbound = InboundMessage(user_id="10001", text="你好")
    state = initialize_graph_state(inbound)

    assert state.inbound.metadata == {}
    assert state.inbound.__class__.__module__.startswith("nonebot_plugin_personal_companion.state")
