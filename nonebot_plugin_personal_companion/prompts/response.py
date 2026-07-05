from __future__ import annotations

from ..state import GraphState


def build_response_prompt(state: GraphState) -> list[dict[str, str]]:
    system_parts = [
        "你是一个通过 LangGraph 驱动的 QQ 陪伴型助手。",
        "根据图状态中的消息、上下文、记忆、工具结果和回复策略生成自然回复。",
    ]

    if state.reply_policy == "ask_clarification":
        system_parts.append("当前策略是询问澄清。请提出一个具体、简短的问题。")
    elif state.reply_policy == "tool_needed":
        system_parts.append("当前策略是工具相关回复。优先根据工具结果或缺失信息回复。")
    elif state.reply_policy == "no_reply":
        system_parts.append("当前策略是不回复。不要生成对用户可见的正文。")
    else:
        system_parts.append("当前策略是正常回复。保持自然、贴近上下文，不要过度展开。")

    user_parts = [f"用户消息：{state.inbound.text}"]

    if state.recent_context:
        user_parts.append("近期上下文：")
        user_parts.extend(f"- {item}" for item in state.recent_context)

    if state.memory.durable_facts:
        user_parts.append("长期事实：")
        user_parts.extend(f"- {item}" for item in state.memory.durable_facts)

    if state.memory.preferences:
        user_parts.append("用户偏好：")
        user_parts.extend(f"- {item}" for item in state.memory.preferences)

    if state.memory.topic_candidates:
        user_parts.append("可延续话题：")
        user_parts.extend(f"- {item}" for item in state.memory.topic_candidates)

    if state.tool_results:
        user_parts.append("工具结果：")
        for result in state.tool_results:
            if result.success:
                content = result.content or "执行成功"
                user_parts.append(f"- {result.tool_name}: {content}")
            else:
                error = result.error or "执行失败"
                user_parts.append(f"- {result.tool_name}: {error}")

    return [
        {"role": "system", "content": "\n".join(system_parts)},
        {"role": "user", "content": "\n".join(user_parts)},
    ]
