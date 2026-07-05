from datetime import date

from nonebot_plugin_personal_companion.memory_graph import MemoryGovernancePolicy, govern_memory


def test_completed_key_memory_is_background_and_forbidden():
    result = govern_memory(
        current_message="今天聊点别的",
        key_memories=[{"content": "用户已经拿到offer了", "memory_type": "event", "status": "completed"}],
    )

    assert result.mentionable_memories == ()
    assert result.background_memories == ("用户已经拿到offer了",)
    assert "拿到offer" not in result.mentionable_memories
    assert result.forbidden_topics


def test_active_preference_is_mentionable():
    result = govern_memory(
        current_message="帮我看一下",
        key_memories=[{"content": "用户喜欢简短建议", "memory_type": "preference", "status": "active"}],
    )

    assert result.mentionable_memories == ("用户喜欢简短建议",)
    assert result.background_memories == ()


def test_future_timeline_is_mentionable_but_past_done_is_background():
    result = govern_memory(
        current_message="今天安排一下",
        timeline_entries=[
            {"event_date": "2026-07-02", "content": "用户准备作品集", "status": "planned"},
            {"event_date": "2026-04-22", "content": "用户宣布自己已经拥有幸福了", "status": "done"},
        ],
        policy=MemoryGovernancePolicy(today=date(2026, 6, 30)),
    )

    assert [item["content"] for item in result.mentionable_timeline] == ["用户准备作品集"]
    assert [item["content"] for item in result.background_timeline] == ["用户宣布自己已经拥有幸福了"]


def test_explicit_history_query_can_mention_past_timeline():
    result = govern_memory(
        current_message="4月22日发生了什么",
        timeline_entries=[{"event_date": "2026-04-22", "content": "用户宣布自己已经拥有幸福了", "status": "done"}],
        policy=MemoryGovernancePolicy(today=date(2026, 6, 30)),
    )

    assert [item["content"] for item in result.mentionable_timeline] == ["用户宣布自己已经拥有幸福了"]
    assert result.background_timeline == ()


def test_proactive_mode_suppresses_non_ongoing_events():
    result = govern_memory(
        current_message="",
        key_memories=[
            {"content": "用户已经解决了申请问题", "memory_type": "event", "status": "completed"},
            {"content": "用户容易因为截止日期焦虑", "memory_type": "emotional_pattern", "status": "active"},
        ],
        policy=MemoryGovernancePolicy(mode="proactive", today=date(2026, 6, 30)),
    )

    assert result.mentionable_memories == ("用户容易因为截止日期焦虑",)
    assert result.background_memories == ("用户已经解决了申请问题",)


def test_recent_proactive_topic_enters_cooldown():
    result = govern_memory(
        current_message="",
        key_memories=[{"content": "用户正在准备作品集", "memory_type": "event", "status": "ongoing"}],
        policy=MemoryGovernancePolicy(mode="proactive", recent_proactive=("作品集那边还顺利吗？",)),
    )

    assert result.mentionable_memories == ()
    assert result.background_memories == ("用户正在准备作品集",)
    assert result.cooldown_topics


def test_suppressed_memory_is_forbidden_not_mentionable():
    result = govern_memory(
        current_message="",
        key_memories=[{"content": "用户不想再提offer", "memory_type": "fact", "status": "suppressed"}],
    )

    assert result.mentionable_memories == ()
    assert result.background_memories == ("用户不想再提offer",)
    assert result.forbidden_topics
