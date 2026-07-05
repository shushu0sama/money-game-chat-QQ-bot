from datetime import datetime, timezone

from nonebot_plugin_personal_companion.graphs import finalize_proactive_output, invoke_proactive_graph
from nonebot_plugin_personal_companion.graphs.proactive import (
    decide_proactive_action_node,
    load_proactive_context_node,
    normalize_proactive_trigger_node,
)
from nonebot_plugin_personal_companion.state import ProactiveState, ProactiveTrigger


def test_invoke_proactive_graph_defaults_to_noop_without_sending():
    trigger = ProactiveTrigger(
        reason="scheduled_check",
        target_user_id="10001",
        current_time=datetime(2026, 6, 28, 12, 0, tzinfo=timezone.utc),
    )

    output = invoke_proactive_graph(trigger)

    assert output.action_type == "none"
    assert output.should_send is False
    assert output.message_text is None
    assert output.diagnostics.run_id
    assert output.diagnostics.visited_nodes == (
        "normalize_proactive_trigger",
        "load_proactive_context",
        "decide_proactive_action",
    )
    assert output.diagnostics.decisions == (
        "proactive_context_loaded:0",
        "proactive_decision:none",
    )


def test_normalize_proactive_trigger_node_strips_fields_and_copies_metadata():
    metadata = {"source": "scheduler"}
    state = ProactiveState(
        trigger=ProactiveTrigger(reason=" scheduled_check ", target_user_id=" 10001 ", metadata=metadata)
    )

    updated = normalize_proactive_trigger_node(state)
    metadata["source"] = "changed"

    assert updated.trigger.reason == "scheduled_check"
    assert updated.trigger.target_user_id == "10001"
    assert updated.trigger.metadata == {"source": "scheduler"}
    assert updated.diagnostics.visited_nodes == ("normalize_proactive_trigger",)


def test_load_proactive_context_node_records_context_count():
    state = ProactiveState(
        trigger=ProactiveTrigger(reason="scheduled_check", target_user_id="10001"),
        user_context=("用户最近在准备申请材料",),
    )

    updated = load_proactive_context_node(state)

    assert updated.user_context == ("用户最近在准备申请材料",)
    assert updated.diagnostics.decisions == ("proactive_context_loaded:1",)
    assert "申请材料" not in updated.diagnostics.decisions[0]


def test_decide_proactive_action_node_is_conservative_by_default():
    state = ProactiveState(
        trigger=ProactiveTrigger(reason="scheduled_check", target_user_id="10001"),
        user_context=("用户最近在准备申请材料",),
        candidate_action="send_message",
        final_decision="send_message",
        message_text="申请材料怎么样了？",
    )

    updated = decide_proactive_action_node(state)

    assert updated.candidate_action == "none"
    assert updated.final_decision == "none"
    assert updated.message_text is None
    assert updated.diagnostics.decisions == ("proactive_decision:none",)


def test_finalize_proactive_output_never_sends_without_send_decision_and_text():
    no_text = ProactiveState(
        trigger=ProactiveTrigger(reason="scheduled_check", target_user_id="10001"),
        final_decision="send_message",
        message_text=None,
    )
    no_send = ProactiveState(
        trigger=ProactiveTrigger(reason="scheduled_check", target_user_id="10001"),
        final_decision="none",
        message_text="你好",
    )

    assert finalize_proactive_output(no_text).should_send is False
    assert finalize_proactive_output(no_send).should_send is False
