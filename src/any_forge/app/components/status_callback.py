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

    def after_llm_call(self, context: Context, *args, **kwargs) -> Context:
        """Update status after LLM calls."""
        span = context.current_span
        attributes: Mapping[str, AttributeValue] = span.attributes
        input_value = str(attributes.get(GenAI.INPUT_MESSAGES, ""))
        output_value = str(attributes.get(GenAI.OUTPUT, ""))

        self._update_status(span.name, input_value, output_value)
        return context

    def after_tool_execution(self, context: Context, *args, **kwargs) -> Context:
        """Update status after tool executions."""
        span = context.current_span
        attributes: Mapping[str, AttributeValue] = span.attributes
        input_value = str(attributes.get(GenAI.TOOL_ARGS, ""))
        output_value = str(attributes.get(GenAI.OUTPUT, ""))

        self._update_status(span.name, input_value, output_value)
        return context

    def _update_status(self, step_name: str, input_value: str, output_value: str):
        """Update the Streamlit status with formatted information."""
        if input_value or output_value:
            message = f"Step: {step_name}\n"
            if input_value:
                message += f"Input: {input_value}\n"
            if output_value:
                message += f"Output: {output_value}"
        else:
            message = f"Step: {step_name}"

        with st.expander(step_name, expanded=True):
            st.write(message)
