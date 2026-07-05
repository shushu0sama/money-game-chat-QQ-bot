from datetime import datetime, timezone

from nonebot_plugin_personal_companion.state import (
    ProactiveOutput,
    ProactiveState,
    ProactiveTrigger,
    initialize_proactive_state,
)


def test_initialize_proactive_state_from_trigger():
    current_time = datetime(2026, 6, 28, 12, 0, tzinfo=timezone.utc)
    trigger = ProactiveTrigger(
        reason="scheduled_check",
        target_user_id="10001",
        current_time=current_time,
        metadata={"source": "scheduler"},
    )

    state = initialize_proactive_state(trigger)

    assert state.trigger == trigger
    assert state.user_context == ()
    assert state.recent_interaction_state == {}
    assert state.candidate_action == "none"
    assert state.final_decision == "none"
    assert state.message_text is None
    assert state.diagnostics.visited_nodes == ()


def test_proactive_trigger_defaults_are_safe_and_independent():
    trigger = ProactiveTrigger(reason="scheduled_check", target_user_id="10001")

    assert trigger.current_time.tzinfo is not None
    assert trigger.metadata == {}


def test_proactive_state_can_hold_context_candidate_and_decision():
    trigger = ProactiveTrigger(reason="scheduled_check", target_user_id="10001")
    state = ProactiveState(
        trigger=trigger,
        user_context=("用户最近在准备申请材料",),
        recent_interaction_state={"last_seen_hours": 12},
        candidate_action="send_message",
        final_decision="send_message",
        message_text="申请材料那边还顺利吗？",
    )

    assert state.user_context == ("用户最近在准备申请材料",)
    assert state.recent_interaction_state == {"last_seen_hours": 12}
    assert state.candidate_action == "send_message"
    assert state.final_decision == "send_message"
    assert state.message_text == "申请材料那边还顺利吗？"


def test_proactive_output_defaults_to_no_send():
    output = ProactiveOutput()

    assert output.action_type == "none"
    assert output.should_send is False
    assert output.message_text is None
    assert output.diagnostics.decisions == ()


def test_proactive_output_can_represent_send_action():
    output = ProactiveOutput(
        action_type="send_message",
        should_send=True,
        message_text="今天状态怎么样？",
    )

    assert output.action_type == "send_message"
    assert output.should_send is True
    assert output.message_text == "今天状态怎么样？"
