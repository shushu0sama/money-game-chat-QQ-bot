from nonebot_plugin_personal_companion.prompts import build_response_prompt
from nonebot_plugin_personal_companion.state import (
    GraphState,
    InboundMessage,
    MemoryResult,
    ToolResult,
)


def test_build_response_prompt_for_normal_reply_includes_message_and_context():
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="继续昨天那个", source="private"),
        recent_context=("昨天聊过申请材料",),
        reply_policy="reply_now",
    )

    messages = build_response_prompt(state)

    assert messages[0]["role"] == "system"
    assert "正常回复" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert "用户消息：继续昨天那个" in messages[1]["content"]
    assert "近期上下文" in messages[1]["content"]
    assert "昨天聊过申请材料" in messages[1]["content"]


def test_build_response_prompt_for_clarification_mode():
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="那个怎么办", source="private"),
        reply_policy="ask_clarification",
    )

    messages = build_response_prompt(state)

    assert "询问澄清" in messages[0]["content"]
    assert "提出一个具体、简短的问题" in messages[0]["content"]


def test_build_response_prompt_for_tool_result_mode():
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="查一下天气", source="private"),
        reply_policy="tool_needed",
        tool_results=(ToolResult(tool_name="search", success=True, content="今天有雨"),),
    )

    messages = build_response_prompt(state)

    assert "工具相关回复" in messages[0]["content"]
    assert "工具结果" in messages[1]["content"]
    assert "search: 今天有雨" in messages[1]["content"]


def test_build_response_prompt_includes_memory_when_available():
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="我该怎么选", source="private"),
        memory=MemoryResult(
            durable_facts=("用户正在准备申请材料",),
            preferences=("用户喜欢简短建议",),
            topic_candidates=("申请材料",),
        ),
        reply_policy="reply_now",
    )

    messages = build_response_prompt(state)
    content = messages[1]["content"]

    assert "长期事实" in content
    assert "用户正在准备申请材料" in content
    assert "用户偏好" in content
    assert "用户喜欢简短建议" in content
    assert "可延续话题" in content
    assert "申请材料" in content


def test_build_response_prompt_excludes_unavailable_optional_sections():
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="你好", source="private"),
        reply_policy="reply_now",
    )

    messages = build_response_prompt(state)
    content = messages[1]["content"]

    assert "近期上下文" not in content
    assert "长期事实" not in content
    assert "用户偏好" not in content
    assert "可延续话题" not in content
    assert "工具结果" not in content


def test_build_response_prompt_includes_tool_error_summary():
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="提醒我", source="private"),
        reply_policy="tool_needed",
        tool_results=(ToolResult(tool_name="reminder", success=False, error="缺少时间"),),
    )

    messages = build_response_prompt(state)

    assert "reminder: 缺少时间" in messages[1]["content"]
