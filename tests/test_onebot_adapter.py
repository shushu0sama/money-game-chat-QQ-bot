from datetime import datetime, timezone

from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, PrivateMessageEvent

from nonebot_plugin_personal_companion.adapters import event_to_inbound_message


def test_event_to_inbound_message_converts_private_event():
    event = PrivateMessageEvent(
        time=1_656_000_000,
        self_id=42,
        post_type="message",
        sub_type="friend",
        user_id=10001,
        message_type="private",
        message_id=123,
        message=Message("  你好  "),
        raw_message="  你好  ",
        font=0,
        sender={"user_id": 10001},
    )

    inbound = event_to_inbound_message(event)

    assert inbound.user_id == "10001"
    assert inbound.group_id is None
    assert inbound.source == "private"
    assert inbound.text == "你好"
    assert inbound.timestamp == datetime.fromtimestamp(1_656_000_000, tz=timezone.utc)
    assert inbound.metadata["message_id"] == 123
    assert inbound.metadata["self_id"] == 42
    assert inbound.metadata["message_type"] == "private"


def test_event_to_inbound_message_converts_group_event():
    event = GroupMessageEvent(
        time=1_656_000_100,
        self_id=42,
        post_type="message",
        sub_type="normal",
        user_id=10001,
        group_id=20002,
        message_type="group",
        message_id=456,
        message=Message(" 群聊消息 "),
        raw_message=" 群聊消息 ",
        font=0,
        sender={"user_id": 10001},
    )

    inbound = event_to_inbound_message(event)

    assert inbound.user_id == "10001"
    assert inbound.group_id == "20002"
    assert inbound.source == "group"
    assert inbound.text == "群聊消息"
    assert inbound.timestamp == datetime.fromtimestamp(1_656_000_100, tz=timezone.utc)
    assert inbound.metadata["message_id"] == 456
    assert inbound.metadata["message_type"] == "group"


def test_event_to_inbound_message_does_not_expose_raw_event():
    event = PrivateMessageEvent(
        time=1_656_000_000,
        self_id=42,
        post_type="message",
        sub_type="friend",
        user_id=10001,
        message_type="private",
        message_id=123,
        message=Message("你好"),
        raw_message="你好",
        font=0,
        sender={"user_id": 10001},
    )

    inbound = event_to_inbound_message(event)

    assert all(value is not event for value in inbound.metadata.values())
