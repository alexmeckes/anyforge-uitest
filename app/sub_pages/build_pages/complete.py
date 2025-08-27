import streamlit as st

from any_forge.state import AgentForgeAgent


def render_complete_step(agent: AgentForgeAgent):
    """Render the complete step."""
    st.markdown("## 🎉 Agent Created Successfully!")
    st.success("Your AI agent has been configured and is ready to use.")
