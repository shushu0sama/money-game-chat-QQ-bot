from nonebot_plugin_personal_companion.nodes import decide_reply_node
from nonebot_plugin_personal_companion.state import GraphState, InboundMessage


def test_decide_reply_node_replies_to_direct_mention():
    state = GraphState(inbound=InboundMessage(user_id="10001", text="艾琳娜你在吗", source="private"))

    updated = decide_reply_node(state)

    assert updated.reply_policy == "reply_now"
    assert updated.intent.label == "chat"
    assert updated.intent.reason == "direct_mention"
    assert updated.diagnostics.visited_nodes == ("decide_reply",)
    assert updated.diagnostics.decisions == ("reply_decision:reply_now:direct_mention",)


def test_decide_reply_node_ignores_group_casual_ack_without_mention():
    state = GraphState(inbound=InboundMessage(user_id="10001", text="嗯嗯", source="group"))

    updated = decide_reply_node(state)

    assert updated.reply_policy == "no_reply"
    assert updated.intent.label == "chat"
    assert updated.intent.reason == "group_casual_ack"


def test_decide_reply_node_asks_clarification_for_ambiguous_message_without_context():
    state = GraphState(inbound=InboundMessage(user_id="10001", text="那个怎么办", source="private"))

    updated = decide_reply_node(state)

    assert updated.reply_policy == "ask_clarification"
    assert updated.intent.label == "chat"
    assert updated.intent.reason == "ambiguous_without_context"


def test_decide_reply_node_replies_to_ambiguous_message_with_context():
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="那个怎么办", source="private"),
        recent_context=("用户昨天说过申请材料卡住了",),
    )

    updated = decide_reply_node(state)

    assert updated.reply_policy == "reply_now"
    assert updated.intent.label == "chat"
    assert updated.intent.reason == "default_chat"


def test_decide_reply_node_routes_tool_like_request():
    state = GraphState(inbound=InboundMessage(user_id="10001", text="明天提醒我交材料", source="private"))

    updated = decide_reply_node(state)

    assert updated.reply_policy == "tool_needed"
    assert updated.intent.label == "tool"
    assert updated.intent.reason == "tool_marker"


def test_decide_reply_node_no_reply_for_empty_message():
    state = GraphState(inbound=InboundMessage(user_id="10001", text="   ", source="private"))

    updated = decide_reply_node(state)

    assert updated.reply_policy == "no_reply"
    assert updated.intent.label == "unknown"
    assert updated.intent.reason == "empty_message"


def test_decide_reply_node_returns_new_state_and_does_not_mutate_original():
    state = GraphState(inbound=InboundMessage(user_id="10001", text="艾琳娜", source="private"))

    updated = decide_reply_node(state)

    assert updated is not state
    assert state.reply_policy == "undecided"
    assert state.diagnostics.visited_nodes == ()
