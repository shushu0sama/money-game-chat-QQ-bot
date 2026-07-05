from nonebot_plugin_personal_companion.memory_graph import EmptyMemoryProvider, StaticMemoryProvider
from nonebot_plugin_personal_companion.state import GraphState, InboundMessage, MemoryResult


def test_empty_memory_provider_returns_empty_memory_result():
    provider = EmptyMemoryProvider()
    state = GraphState(inbound=InboundMessage(user_id="10001", text="你好"))

    memory = provider.retrieve_memory(state)

    assert memory == MemoryResult()
    assert memory.recent_context == ()
    assert memory.durable_facts == ()
    assert memory.preferences == ()
    assert memory.topic_candidates == ()


def test_static_memory_provider_returns_populated_memory_result():
    expected = MemoryResult(
        recent_context=("昨天聊过申请材料",),
        durable_facts=("用户正在准备申请材料",),
        preferences=("用户喜欢简短建议",),
        topic_candidates=("申请材料",),
    )
    provider = StaticMemoryProvider(expected)
    state = GraphState(inbound=InboundMessage(user_id="10001", text="继续昨天那个"))

    memory = provider.retrieve_memory(state)

    assert memory == expected
    assert provider.calls == [state]


def test_memory_result_distinguishes_memory_categories():
    memory = MemoryResult(
        recent_context=("最近一次对话",),
        durable_facts=("长期事实",),
        preferences=("用户偏好",),
        topic_candidates=("可延续话题",),
    )

    assert memory.recent_context == ("最近一次对话",)
    assert memory.durable_facts == ("长期事实",)
    assert memory.preferences == ("用户偏好",)
    assert memory.topic_candidates == ("可延续话题",)
