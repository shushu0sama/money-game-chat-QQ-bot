from nonebot_plugin_personal_companion.nodes import generate_response_node
from nonebot_plugin_personal_companion.state import GraphState, InboundMessage


class FakeResponseLLMClient:
    def __init__(self, response: str | None):
        self.response = response
        self.calls = []

    def generate_response(self, messages: list[dict[str, str]]) -> str | None:
        self.calls.append(messages)
        return self.response


def test_generate_response_node_uses_fake_llm_for_normal_reply():
    llm = FakeResponseLLMClient("  你好呀  ")
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="艾琳娜你在吗"),
        reply_policy="reply_now",
    )

    updated = generate_response_node(state, llm)

    assert updated.generated_response.text == "你好呀"
    assert updated.generated_response.mode == "reply_now"
    assert len(llm.calls) == 1
    assert "用户消息：艾琳娜你在吗" in llm.calls[0][1]["content"]
    assert updated.diagnostics.visited_nodes == ("generate_response",)
    assert updated.diagnostics.decisions == ("response_generated:reply_now:True",)


def test_generate_response_node_uses_clarification_mode():
    llm = FakeResponseLLMClient("你说的是申请材料那件事吗？")
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="那个怎么办"),
        reply_policy="ask_clarification",
    )

    updated = generate_response_node(state, llm)

    assert updated.generated_response.text == "你说的是申请材料那件事吗？"
    assert updated.generated_response.mode == "ask_clarification"
    assert "询问澄清" in llm.calls[0][0]["content"]


def test_generate_response_node_skips_llm_for_no_reply():
    llm = FakeResponseLLMClient("不应该调用")
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="嗯嗯", source="group"),
        reply_policy="no_reply",
    )

    updated = generate_response_node(state, llm)

    assert updated.generated_response.text is None
    assert updated.generated_response.mode == "no_reply"
    assert llm.calls == []
    assert updated.diagnostics.decisions == ("response_generated:no_reply",)


def test_generate_response_node_handles_empty_llm_response():
    llm = FakeResponseLLMClient(None)
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="你好"),
        reply_policy="reply_now",
    )

    updated = generate_response_node(state, llm)

    assert updated.generated_response.text is None
    assert updated.generated_response.mode == "reply_now"
    assert updated.diagnostics.decisions == ("response_generated:reply_now:False",)


def test_generate_response_node_returns_new_state_and_does_not_mutate_original():
    llm = FakeResponseLLMClient("你好")
    state = GraphState(inbound=InboundMessage(user_id="10001", text="你好"), reply_policy="reply_now")

    updated = generate_response_node(state, llm)

    assert updated is not state
    assert state.generated_response.text is None
    assert state.diagnostics.visited_nodes == ()
