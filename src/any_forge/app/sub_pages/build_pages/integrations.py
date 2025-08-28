import streamlit as st

from any_forge.state import AgentForgeAgent
from any_forge.tools.integrations import SUPPORTED_INTEGRATIONS


def render_integrations(agent: AgentForgeAgent) -> None:
    """Render the integrations step."""
    st.markdown("## Select Integrations")
    st.write("This is where we would narrow down which integrations the agent will have access to..")
    # display a bubble for each integration, which you can expand to see the tools available
    selected_integrations = st.multiselect("Select Integrations", SUPPORTED_INTEGRATIONS, key="integrations")
    agent.integrations = selected_integrations
