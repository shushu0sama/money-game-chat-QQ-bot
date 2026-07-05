from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent

from ..state import InboundMessage


def event_to_inbound_message(event: PrivateMessageEvent | GroupMessageEvent) -> InboundMessage:
    source = "group" if isinstance(event, GroupMessageEvent) else "private"
    group_id = str(event.group_id) if isinstance(event, GroupMessageEvent) else None
    timestamp = _event_timestamp(event)
    return InboundMessage(
        user_id=str(event.user_id),
        group_id=group_id,
        source=source,
        text=event.get_plaintext().strip(),
        timestamp=timestamp,
        metadata=_event_metadata(event),
    )


def _event_timestamp(event: PrivateMessageEvent | GroupMessageEvent) -> datetime:
    raw_time = getattr(event, "time", None)
    if isinstance(raw_time, int | float):
        return datetime.fromtimestamp(raw_time, tz=timezone.utc)
    return datetime.now(timezone.utc)


def _event_metadata(event: PrivateMessageEvent | GroupMessageEvent) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "message_id": getattr(event, "message_id", None),
        "self_id": getattr(event, "self_id", None),
        "post_type": getattr(event, "post_type", None),
        "message_type": getattr(event, "message_type", None),
        "sub_type": getattr(event, "sub_type", None),
    }
    return {key: value for key, value in metadata.items() if value is not None}
