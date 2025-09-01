# mypy: disable-error-code="attr-defined,index,no-untyped-def"

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st
from any_agent.callbacks import Callback, Context
from any_agent.tracing.attributes import GenAI

if TYPE_CHECKING:
    from collections.abc import Mapping

    from any_agent.tracing.otel_types import AttributeValue


class StreamlitStatusCallback(Callback):
    """Callback to update Streamlit status with agent progress."""

    def __init__(self, container):
        """Initialize the StreamlitStatusCallback."""
        self.container = container
        super().__init__()

    def after_llm_call(self, context: Context, *args, **kwargs) -> Context:
        """Update status after LLM calls."""
        span = context.current_span
        attributes: Mapping[str, AttributeValue] = span.attributes
        output_value = str(attributes.get(GenAI.OUTPUT, ""))
        st.session_state.messages.append({"role": "assistant", "content": output_value})
        self.container.chat_message("assistant").write(output_value)
        return context

    def after_tool_execution(self, context: Context, *args, **kwargs) -> Context:
        """Update status after tool executions."""
        span = context.current_span
        attributes: Mapping[str, AttributeValue] = span.attributes
        output_value = str(attributes.get(GenAI.OUTPUT, ""))
        st.session_state.messages.append({"role": "assistant", "content": output_value, "avatar": "🛠️"})
        self.container.chat_message("assistant", avatar="🛠️").write(output_value)
        return context
