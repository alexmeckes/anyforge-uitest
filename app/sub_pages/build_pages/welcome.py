import streamlit as st

from any_forge.state import AgentStateMachine


def render_welcome_step(agent_state: AgentStateMachine) -> None:
    """Render the welcome step."""
    st.markdown("Click **Next** to begin.")
    st.write("This is where you would start building a new agent, or resume an agent build that is in progress.")
