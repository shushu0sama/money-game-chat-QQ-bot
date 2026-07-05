from __future__ import annotations

from dataclasses import replace

from ..state import GraphState, IntentClassification, record_decision, record_node_visit

_DIRECT_MENTION_MARKERS = ("艾琳娜", "bot", "机器人", "你")
_TOOL_MARKERS = (
    "提醒我",
    "帮我提醒",
    "定时",
    "日历",
    "搜索",
    "查一下",
    "帮我查",
    "几点",
    "几号",
    "星期几",
)
_AMBIGUOUS_MARKERS = ("那个", "这件事", "之前那个", "继续", "怎么办")
_CASUAL_ACKS = ("嗯", "嗯嗯", "哦", "好", "好的", "哈哈", "哈哈哈", "收到")


def decide_reply_node(state: GraphState) -> GraphState:
    text = state.inbound.text.strip()
    policy = "reply_now"
    intent = IntentClassification(label="chat", confidence=0.6, reason="default_chat")

    if not text:
        policy = "no_reply"
        intent = IntentClassification(label="unknown", confidence=1.0, reason="empty_message")
    elif _is_tool_like(text):
        policy = "tool_needed"
        intent = IntentClassification(label="tool", confidence=0.8, reason="tool_marker")
    elif _is_ambiguous(text) and not state.recent_context:
        policy = "ask_clarification"
        intent = IntentClassification(label="chat", confidence=0.5, reason="ambiguous_without_context")
    elif _is_casual_ack(text) and state.inbound.source == "group" and not _is_direct_mention(text):
        policy = "no_reply"
        intent = IntentClassification(label="chat", confidence=0.7, reason="group_casual_ack")
    elif _is_direct_mention(text):
        policy = "reply_now"
        intent = IntentClassification(label="chat", confidence=0.9, reason="direct_mention")

    updated = replace(state, intent=intent, reply_policy=policy)
    updated = record_node_visit(updated, "decide_reply")
    return record_decision(updated, f"reply_decision:{policy}:{intent.reason}")


def _is_direct_mention(text: str) -> bool:
    return any(marker in text for marker in _DIRECT_MENTION_MARKERS)


def _is_tool_like(text: str) -> bool:
    return any(marker in text for marker in _TOOL_MARKERS)


def _is_ambiguous(text: str) -> bool:
    return any(marker in text for marker in _AMBIGUOUS_MARKERS) and len(text) <= 12


def _is_casual_ack(text: str) -> bool:
    return text in _CASUAL_ACKS
