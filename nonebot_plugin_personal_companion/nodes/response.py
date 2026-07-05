from __future__ import annotations

from dataclasses import replace
from typing import Protocol

from ..prompts import build_response_prompt
from ..state import GeneratedResponse, GraphState, record_decision, record_node_visit


class ResponseLLMClient(Protocol):
    def generate_response(self, messages: list[dict[str, str]]) -> str | None: ...


def generate_response_node(state: GraphState, llm_client: ResponseLLMClient) -> GraphState:
    updated = record_node_visit(state, "generate_response")

    if state.reply_policy == "no_reply":
        updated = replace(updated, generated_response=GeneratedResponse(text=None, mode="no_reply"))
        return record_decision(updated, "response_generated:no_reply")

    messages = build_response_prompt(updated)
    response_text = llm_client.generate_response(messages)
    response_text = response_text.strip() if response_text else None
    mode = state.reply_policy if state.reply_policy != "undecided" else "reply_now"
    updated = replace(updated, generated_response=GeneratedResponse(text=response_text, mode=mode))
    return record_decision(updated, f"response_generated:{mode}:{bool(response_text)}")
