from enum import StrEnum

import streamlit as st

from any_forge.state.state import AgentStateMachine


class AgentPage(StrEnum):
    """Enum for the different pages of the agent builder. Right now just build."""

    BUILD = "build"


def initialize_state_machine() -> AgentStateMachine:
    """Initialize or retrieve the state machine from session state.

    Returns:
        AgentStateMachine: The state machine.

    """
    if "agent_state_machine" not in st.session_state:
        st.session_state.agent_state_machine = AgentStateMachine()
    return st.session_state.agent_state_machine
