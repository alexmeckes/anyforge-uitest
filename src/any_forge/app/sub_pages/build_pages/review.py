import streamlit as st

from any_forge.state import AgentForgeAgent


def render_review_step(agent: AgentForgeAgent) -> None:
    """Render the review step."""
    st.markdown("## Review Configuration")
    st.write("This is where you would run and review how the agent is doing before you finalize")
