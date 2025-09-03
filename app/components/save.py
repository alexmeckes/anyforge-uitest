import streamlit as st

from any_forge.state import AgentForgeAgent
from any_forge.storage import save_agents
from app.state import get_state


@st.fragment
def render_save(agent: AgentForgeAgent) -> None:
    """Render the save step."""
    st.subheader("Save the Agent")

    if st.button("Save", key="save_btn"):
        state = get_state()

        save_agents(state.development_agents, state.completed_agents)
        st.success("Agent saved!")
