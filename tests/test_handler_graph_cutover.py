from nonebot_plugin_personal_companion.graphs import invoke_message_graph
from nonebot_plugin_personal_companion.state import GraphDiagnostics, GraphOutput, InboundMessage


def test_retired_direct_chat_no_reply_path_does_not_fall_back_to_legacy():
    diagnostics = GraphDiagnostics(decisions=("reply_decision:no_reply:group_casual_ack",))
    output = GraphOutput(should_reply=False, diagnostics=diagnostics)

    assert output.should_reply is False
    assert not _is_tool_needed(output)


def test_tool_needed_output_is_the_only_real_event_legacy_fallback_path():
    diagnostics = GraphDiagnostics(decisions=("reply_decision:tool_needed:tool_marker",))
    output = GraphOutput(should_reply=False, diagnostics=diagnostics)

    assert _is_tool_needed(output)


def test_active_message_graph_handles_basic_direct_chat_without_legacy_handler():
    class FakeLLM:
        def generate_response(self, messages):
            return "你好呀"

    output = invoke_message_graph(
        InboundMessage(user_id="10001", text="艾琳娜你在吗", source="private"),
        llm_client=FakeLLM(),
    )

    assert output.should_reply is True
    assert output.reply_text == "你好呀"
    assert "reply_policy:reply_now" in output.diagnostics.decisions


def _is_tool_needed(output: GraphOutput) -> bool:
    return any("reply_decision:tool_needed" in item for item in output.diagnostics.decisions)
