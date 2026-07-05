from nonebot_plugin_personal_companion.nodes import normalize_input_node
from nonebot_plugin_personal_companion.state import GraphState, InboundMessage


def test_normalize_input_node_strips_private_message_text_and_user_id():
    state = GraphState(
        inbound=InboundMessage(
            user_id=" 10001 ",
            source="private",
            text="  你好呀  ",
            metadata={"message_id": "abc"},
        )
    )

    updated = normalize_input_node(state)

    assert updated.inbound.user_id == "10001"
    assert updated.inbound.text == "你好呀"
    assert updated.inbound.source == "private"
    assert updated.inbound.metadata == {"message_id": "abc"}
    assert updated.diagnostics.visited_nodes == ("normalize_input",)


def test_normalize_input_node_strips_group_id_and_preserves_timestamp():
    state = GraphState(
        inbound=InboundMessage(
            user_id="10001",
            group_id=" 20002 ",
            source="group",
            text=" 群聊消息 ",
        )
    )

    updated = normalize_input_node(state)

    assert updated.inbound.group_id == "20002"
    assert updated.inbound.source == "group"
    assert updated.inbound.text == "群聊消息"
    assert updated.inbound.timestamp == state.inbound.timestamp


def test_normalize_input_node_returns_new_state_and_does_not_mutate_original():
    state = GraphState(inbound=InboundMessage(user_id="10001", text=" 你好 "))

    updated = normalize_input_node(state)

    assert updated is not state
    assert updated.inbound is not state.inbound
    assert state.inbound.text == " 你好 "
    assert state.diagnostics.visited_nodes == ()


def test_normalize_input_node_copies_metadata():
    metadata = {"message_id": "abc"}
    state = GraphState(inbound=InboundMessage(user_id="10001", text="你好", metadata=metadata))

    updated = normalize_input_node(state)
    metadata["message_id"] = "changed"

    assert updated.inbound.metadata == {"message_id": "abc"}
