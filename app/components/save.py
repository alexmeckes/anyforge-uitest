import streamlit as st

from any_forge.state import AgentForgeAgent
from any_forge.storage import save_agents


@st.fragment
def render_save(agent: AgentForgeAgent) -> None:
    """Render the save step."""
    st.subheader("Save the Agent")

    if st.button("Save", key="save_btn"):
        save_agents(st.session_state["agents"])
        st.success("Agent saved!")
