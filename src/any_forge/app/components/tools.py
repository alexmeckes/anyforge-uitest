import streamlit as st

from any_forge.generation.tools import get_recommended_tools
from any_forge.state import AgentForgeAgent


@st.fragment
def render_tools(agent: AgentForgeAgent) -> None:
    """Render the tools step."""
    assert agent.task_description is not None
    st.subheader("Tools")
    with st.spinner("Generating recommended tools..."):
        recommended_tools = get_recommended_tools(agent.task_description, agent.integrations)
        st.write([{t["function"]["name"]: t["function"]["description"]} for t in recommended_tools])
    agent.tools = recommended_tools
