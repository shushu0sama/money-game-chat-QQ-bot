from nonebot_plugin_personal_companion.memory_graph import StaticMemoryProvider
from nonebot_plugin_personal_companion.nodes import retrieve_memory_node
from nonebot_plugin_personal_companion.state import GraphState, InboundMessage, MemoryResult


def test_retrieve_memory_node_writes_memory_from_provider():
    memory = MemoryResult(
        recent_context=("昨天聊过申请材料",),
        durable_facts=("用户正在准备申请材料",),
        preferences=("用户喜欢简短建议",),
        topic_candidates=("申请材料",),
    )
    provider = StaticMemoryProvider(memory)
    state = GraphState(inbound=InboundMessage(user_id="10001", text="继续昨天那个"))

    updated = retrieve_memory_node(state, provider=provider)

    assert updated.memory == memory
    assert provider.calls == [state]


def test_retrieve_memory_node_records_summary_without_memory_content():
    memory = MemoryResult(
        recent_context=("敏感近期上下文", "另一条上下文"),
        durable_facts=("长期事实",),
        preferences=("用户偏好",),
        topic_candidates=("话题一", "话题二"),
    )
    state = GraphState(inbound=InboundMessage(user_id="10001", text="继续"))

    updated = retrieve_memory_node(state, provider=StaticMemoryProvider(memory))

    assert updated.diagnostics.visited_nodes == ("retrieve_memory",)
    assert updated.diagnostics.decisions == ("memory_loaded:recent=2:facts=1:preferences=1:topics=2",)
    assert "敏感" not in updated.diagnostics.decisions[0]
    assert "长期事实" not in updated.diagnostics.decisions[0]


def test_retrieve_memory_node_defaults_to_empty_provider():
    state = GraphState(inbound=InboundMessage(user_id="10001", text="你好"))

    updated = retrieve_memory_node(state)

    assert updated.memory == MemoryResult()
    assert updated.diagnostics.decisions == ("memory_loaded:recent=0:facts=0:preferences=0:topics=0",)


def test_retrieve_memory_node_returns_new_state_and_does_not_mutate_original():
    memory = MemoryResult(durable_facts=("用户正在准备申请材料",))
    state = GraphState(inbound=InboundMessage(user_id="10001", text="继续"))

    updated = retrieve_memory_node(state, provider=StaticMemoryProvider(memory))

    assert updated is not state
    assert state.memory == MemoryResult()
    assert state.diagnostics.visited_nodes == ()
