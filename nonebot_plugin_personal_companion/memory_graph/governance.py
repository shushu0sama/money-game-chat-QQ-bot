from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

from ..memory import BEIJING_TZ

GovernanceMode = Literal["chat", "proactive", "explicit_history"]


@dataclass(frozen=True)
class GovernedMemoryResult:
    mentionable_memories: tuple[str, ...] = ()
    background_memories: tuple[str, ...] = ()
    forbidden_topics: tuple[str, ...] = ()
    cooldown_topics: tuple[str, ...] = ()
    mentionable_timeline: tuple[dict, ...] = ()
    background_timeline: tuple[dict, ...] = ()


@dataclass(frozen=True)
class MemoryGovernancePolicy:
    mode: GovernanceMode = "chat"
    today: date | None = None
    recent_messages: tuple[str, ...] = ()
    recent_proactive: tuple[str, ...] = ()


def govern_memory(
    *,
    current_message: str,
    key_memories: list[dict] | tuple[dict, ...] = (),
    timeline_entries: list[dict] | tuple[dict, ...] = (),
    policy: MemoryGovernancePolicy | None = None,
) -> GovernedMemoryResult:
    policy = policy or MemoryGovernancePolicy()
    today = policy.today or datetime.now(BEIJING_TZ).date()
    explicit = policy.mode == "explicit_history" or _explicitly_reopens_history(current_message)
    cooldown_topics = _extract_cooldown_topics(policy.recent_messages + policy.recent_proactive)

    mentionable_memories: list[str] = []
    background_memories: list[str] = []
    forbidden_topics: list[str] = []
    for memory in key_memories:
        content = str(memory.get("content") or "").strip()
        if not content:
            continue
        memory_type = memory.get("memory_type") or "fact"
        status = memory.get("status") or "active"
        topic_tokens = _topic_tokens(content)

        if _is_forbidden_memory(memory_type, status):
            background_memories.append(content)
            forbidden_topics.extend(topic_tokens)
            continue

        if _has_cooldown_topic(topic_tokens, cooldown_topics):
            background_memories.append(content)
            continue

        if policy.mode == "proactive" and memory_type == "event" and status != "ongoing":
            background_memories.append(content)
            continue

        mentionable_memories.append(content)

    mentionable_timeline: list[dict] = []
    background_timeline: list[dict] = []
    for entry in timeline_entries:
        status = entry.get("status") or "planned"
        topic_tokens = _topic_tokens(str(entry.get("content") or ""))
        event_date = _parse_event_date(entry.get("event_date"))
        is_today_or_future = event_date is not None and event_date >= today

        if status == "suppressed":
            background_timeline.append(entry)
            forbidden_topics.extend(topic_tokens)
            continue

        if _has_cooldown_topic(topic_tokens, cooldown_topics):
            background_timeline.append(entry)
            continue

        if explicit:
            mentionable_timeline.append(entry)
            continue

        if status in {"planned", "ongoing"} and is_today_or_future:
            mentionable_timeline.append(entry)
        else:
            background_timeline.append(entry)
            if status in {"done", "completed", "cancelled", "expired"}:
                forbidden_topics.extend(topic_tokens)

    return GovernedMemoryResult(
        mentionable_memories=tuple(_dedupe(mentionable_memories)),
        background_memories=tuple(_dedupe(background_memories)),
        forbidden_topics=tuple(_dedupe(forbidden_topics)),
        cooldown_topics=tuple(_dedupe(cooldown_topics)),
        mentionable_timeline=tuple(mentionable_timeline),
        background_timeline=tuple(background_timeline),
    )


def _is_forbidden_memory(memory_type: str, status: str) -> bool:
    if memory_type == "event" and status in {"completed", "expired", "suppressed"}:
        return True
    if memory_type == "manifestation" and status in {"released", "fulfilled", "expired", "suppressed"}:
        return True
    return status == "suppressed"


def _explicitly_reopens_history(text: str) -> bool:
    return bool(re.search(r"\d{1,2}月\d{1,2}[日号]?|20\d{2}[-/.年]\d{1,2}[-/.月]\d{1,2}|之前那个|那件事|上次|那次", text))


def _parse_event_date(value) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value)).date()
    except ValueError:
        return None


def _extract_cooldown_topics(texts: tuple[str, ...]) -> tuple[str, ...]:
    topics: list[str] = []
    for text in texts:
        topics.extend(_topic_tokens(text))
    return tuple(_dedupe(topics))


def _has_cooldown_topic(topic_tokens: list[str], cooldown_topics: tuple[str, ...]) -> bool:
    return any(
        token == cooldown
        or token in cooldown
        or cooldown in token
        or _has_shared_phrase(token, cooldown)
        for token in topic_tokens
        for cooldown in cooldown_topics
    )


def _has_shared_phrase(left: str, right: str) -> bool:
    if len(left) < 2 or len(right) < 2:
        return False
    fragments = {left[index:index + 2] for index in range(len(left) - 1)}
    return any(fragment in right for fragment in fragments)


def _topic_tokens(text: str) -> list[str]:
    candidates = re.findall(r"[一-鿿A-Za-z0-9]{2,}", text)
    stopwords = {"用户", "已经", "之前", "今天", "明天", "这个", "那个", "事情", "提醒", "主动", "最近", "正在", "准备", "那边", "顺利"}
    return [candidate[:12] for candidate in candidates if candidate not in stopwords]


def _topic_from_text(text: str) -> str | None:
    tokens = _topic_tokens(text)
    return tokens[0] if tokens else None


def _dedupe(items):
    seen = set()
    result = []
    for item in items:
        key = repr(item)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
