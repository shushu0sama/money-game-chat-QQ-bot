from dataclasses import replace

from nonebot_plugin_personal_companion.state import (
    GraphDiagnostics,
    GraphState,
    InboundMessage,
    ToolPlan,
    ensure_run_id,
    record_decision,
    record_error,
    record_node_visit,
    record_reply_policy,
    record_tool_plan,
    summarize_tool_plan,
)


def test_ensure_run_id_adds_run_id_without_changing_existing_fields():
    state = GraphState(inbound=InboundMessage(user_id="10001", text="你好"))

    updated = ensure_run_id(state)

    assert updated.diagnostics.run_id
    assert updated.inbound == state.inbound
    assert state.diagnostics.run_id is None


def test_ensure_run_id_keeps_existing_run_id():
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="你好"),
        diagnostics=GraphDiagnostics(run_id="existing"),
    )

    updated = ensure_run_id(state)

    assert updated.diagnostics.run_id == "existing"


def test_record_node_visit_appends_visited_node():
    state = GraphState(inbound=InboundMessage(user_id="10001", text="你好"))

    updated = record_node_visit(record_node_visit(state, "input"), "decision")

    assert updated.diagnostics.visited_nodes == ("input", "decision")


def test_record_decision_appends_decision():
    state = GraphState(inbound=InboundMessage(user_id="10001", text="你好"))

    updated = record_decision(record_decision(state, "reply_now"), "normal_response")

    assert updated.diagnostics.decisions == ("reply_now", "normal_response")


def test_summarize_tool_plan_without_tool_avoids_arguments():
    tool_plan = ToolPlan(rejection_reason="unmatched")

    assert summarize_tool_plan(tool_plan) == "no_tool:unmatched"


def test_record_tool_plan_uses_summary_without_sensitive_arguments():
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="提醒我交材料"),
        tool_plan=ToolPlan(
            tool_name="reminder",
            arguments={"secret": "do not log"},
            confidence=0.876,
            requires_confirmation=True,
        ),
    )

    updated = record_tool_plan(state)

    assert updated.diagnostics.decisions == ("tool:reminder:confidence=0.88:confirm",)
    assert "secret" not in updated.diagnostics.decisions[0]


def test_record_reply_policy_adds_final_policy_decision():
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="你好"),
        reply_policy="no_reply",
    )

    updated = record_reply_policy(state)

    assert updated.diagnostics.decisions == ("reply_policy:no_reply",)


def test_record_error_preserves_run_id_nodes_and_decisions():
    state = GraphState(
        inbound=InboundMessage(user_id="10001", text="你好"),
        diagnostics=GraphDiagnostics(
            run_id="run-1",
            visited_nodes=("input",),
            decisions=("reply_now",),
        ),
    )

    updated = record_error(state, RuntimeError("boom"))

    assert updated.diagnostics.run_id == "run-1"
    assert updated.diagnostics.visited_nodes == ("input",)
    assert updated.diagnostics.decisions == ("reply_now",)
    assert updated.diagnostics.error == "boom"


def test_helpers_return_new_state_instances():
    state = GraphState(inbound=InboundMessage(user_id="10001", text="你好"))

    updated = record_node_visit(state, "input")

    assert updated is not state
    assert state.diagnostics.visited_nodes == ()
