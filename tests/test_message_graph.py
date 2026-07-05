from nonebot_plugin_personal_companion.graphs import finalize_message_output, invoke_message_graph
from nonebot_plugin_personal_companion.state import GeneratedResponse, GraphState, InboundMessage


class FakeResponseLLMClient:
    def __init__(self, response: str | None):
        self.response = response
        self.calls = []

    def generate_response(self, messages: list[dict[str, str]]) -> str | None:
        self.calls.append(messages)
        return self.response


class FakeRecentContextProvider:
    def load_recent_context(self, user_id: str, limit: int = 8) -> tuple[str, ...]:
        return ("昨天聊过申请材料",)


def test_invoke_message_graph_returns_reply_output_without_nonebot():
    llm = FakeResponseLLMClient("你好呀")
    inbound = InboundMessage(user_id="10001", text="艾琳娜你在吗", source="private")

    output = invoke_message_graph(inbound, llm_client=llm, context_provider=FakeRecentContextProvider())

    assert output.should_reply is True
    assert output.reply_text == "你好呀"
    assert output.diagnostics.run_id
    assert output.diagnostics.visited_nodes == (
        "normalize_input",
        "load_context",
        "decide_reply",
        "generate_response",
    )
    assert "reply_policy:reply_now" in output.diagnostics.decisions
    assert len(llm.calls) == 1


def test_invoke_message_graph_returns_no_reply_for_group_casual_ack():
    llm = FakeResponseLLMClient("不应该调用")
    inbound = InboundMessage(user_id="10001", text="嗯嗯", source="group")

    output = invoke_message_graph(inbound, llm_client=llm)

    assert output.should_reply is False
    assert output.reply_text is None
    assert output.diagnostics.run_id
    assert output.diagnostics.decisions[-1] == "response_generated:no_reply"
    assert llm.calls == []


def test_invoke_message_graph_can_ask_clarification():
    llm = FakeResponseLLMClient("你说的是哪件事？")
    inbound = InboundMessage(user_id="10001", text="那个怎么办", source="private")

    output = invoke_message_graph(inbound, llm_client=llm)

    assert output.should_reply is True
    assert output.reply_text == "你说的是哪件事？"
    assert "reply_policy:ask_clarification" in output.diagnostics.decisions


def test_finalize_message_output_requires_reply_text():
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="你好"),
        reply_policy="reply_now",
        generated_response=GeneratedResponse(text=None, mode="reply_now"),
    )

    output = finalize_message_output(state)

    assert output.should_reply is False
    assert output.reply_text is None
