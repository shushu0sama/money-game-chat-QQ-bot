from datetime import datetime, timezone

from nonebot_plugin_personal_companion.state import (
    GraphAction,
    GraphDiagnostics,
    GraphOutput,
    InboundMessage,
)


def test_inbound_message_can_be_created_without_nonebot():
    timestamp = datetime(2026, 6, 28, 12, 0, tzinfo=timezone.utc)

    message = InboundMessage(
        user_id="10001",
        group_id="20002",
        source="group",
        text="你好",
        timestamp=timestamp,
        metadata={"message_id": "abc"},
    )

    assert message.user_id == "10001"
    assert message.group_id == "20002"
    assert message.source == "group"
    assert message.text == "你好"
    assert message.timestamp == timestamp
    assert message.metadata == {"message_id": "abc"}


def test_inbound_message_defaults_are_nonebot_independent():
    message = InboundMessage(user_id="10001", text="你好")

    assert message.source == "unknown"
    assert message.group_id is None
    assert message.metadata == {}
    assert message.timestamp.tzinfo is not None


def test_graph_output_contains_reply_action_and_diagnostics():
    output = GraphOutput(
        should_reply=True,
        reply_text="你好呀",
        actions=(GraphAction(type="send_message", payload={"channel": "private"}),),
        diagnostics=GraphDiagnostics(
            run_id="run-1",
            visited_nodes=("input", "response"),
            decisions=("reply_now",),
        ),
    )

    assert output.should_reply is True
    assert output.reply_text == "你好呀"
    assert output.actions[0].type == "send_message"
    assert output.actions[0].payload == {"channel": "private"}
    assert output.diagnostics.run_id == "run-1"
    assert output.diagnostics.visited_nodes == ("input", "response")
    assert output.diagnostics.decisions == ("reply_now",)


def test_graph_output_defaults_to_no_actions_and_empty_diagnostics():
    output = GraphOutput(should_reply=False)

    assert output.reply_text is None
    assert output.actions == ()
    assert output.diagnostics.visited_nodes == ()
    assert output.diagnostics.decisions == ()
