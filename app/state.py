from typing import Any

import streamlit as st
from any_agent.evaluation.schemas import EvaluationOutput
from pydantic import BaseModel, Field

from any_forge.integrations import AuthStatus
from any_forge.state import AgentForgeAgent

STATE_KEY = "state"


class StreamlitState(BaseModel):
    """Streamlit state."""

    development_agents: dict[str, AgentForgeAgent] = Field(default_factory=dict)

    completed_agents: dict[str, AgentForgeAgent] = Field(default_factory=dict)

    auth_statuses: list[AuthStatus] = Field(default_factory=list)

    evaluation_results: list[EvaluationOutput] = Field(default_factory=list)

    gen_instructions: str | None = None

    should_regenerate_instructions: bool = Field(default=False)

    should_regenerate_tools: bool = Field(default=False)

    task_description: str | None = None

    recommended_tool_names: list[str] = Field(default_factory=list)

    messages: list[dict[str, Any]] = Field(default_factory=list)

    delete_confirmation: bool = Field(default=False)

    selected_agent_id: str | None = None


def get_state() -> StreamlitState:
    """Get the streamlit state."""
    state = st.session_state[STATE_KEY]
    if not state:
        err_msg = f"{STATE_KEY} was not properly initialized"
        raise ValueError(err_msg)
    if not isinstance(state, StreamlitState):
        err_msg = f"Unexpected type for {STATE_KEY}: {type(state)}"
        raise ValueError(err_msg)
    return state
