import streamlit as st

from any_forge.state import AgentForgeAgent


def render_welcome_step(agent: AgentForgeAgent) -> None:
    """Render the welcome step."""
    st.markdown("Click **Next** to begin.")
    st.write("This is where you would start building a new agent, or resume an agent build that is in progress.")
