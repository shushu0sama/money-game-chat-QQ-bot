from nonebot_plugin_personal_companion.nodes import EmptyRecentContextProvider, load_context_node
from nonebot_plugin_personal_companion.state import GraphState, InboundMessage


class FakeRecentContextProvider:
    def __init__(self):
        self.calls = []

    def load_recent_context(self, user_id: str, limit: int = 8) -> tuple[str, ...]:
        self.calls.append((user_id, limit))
        return ("昨天聊过申请材料", "用户希望回复简短一点")


def test_load_context_node_writes_recent_context_from_provider():
    provider = FakeRecentContextProvider()
    state = GraphState(inbound=InboundMessage(user_id="10001", text="继续昨天那个"))

    updated = load_context_node(state, provider=provider, limit=2)

    assert updated.recent_context == ("昨天聊过申请材料", "用户希望回复简短一点")
    assert provider.calls == [("10001", 2)]


def test_load_context_node_records_diagnostics_summary_without_full_context():
    provider = FakeRecentContextProvider()
    state = GraphState(inbound=InboundMessage(user_id="10001", text="继续昨天那个"))

    updated = load_context_node(state, provider=provider)

    assert updated.diagnostics.visited_nodes == ("load_context",)
    assert updated.diagnostics.decisions == ("context_loaded:2",)
    assert "申请材料" not in updated.diagnostics.decisions[0]


def test_load_context_node_defaults_to_empty_provider():
    state = GraphState(inbound=InboundMessage(user_id="10001", text="你好"))

    updated = load_context_node(state)

    assert updated.recent_context == ()
    assert updated.diagnostics.decisions == ("context_loaded:0",)


def test_empty_recent_context_provider_returns_empty_tuple():
    provider = EmptyRecentContextProvider()

    assert provider.load_recent_context("10001") == ()


def test_load_context_node_returns_new_state_and_does_not_mutate_original():
    provider = FakeRecentContextProvider()
    state = GraphState(inbound=InboundMessage(user_id="10001", text="继续昨天那个"))

    updated = load_context_node(state, provider=provider)

    assert updated is not state
    assert state.recent_context == ()
    assert state.diagnostics.visited_nodes == ()
