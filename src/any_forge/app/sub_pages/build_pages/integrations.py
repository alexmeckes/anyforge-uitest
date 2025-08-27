import streamlit as st

from any_forge.state import AgentForgeAgent
from any_forge.tools.integrations import SUPPORTED_INTEGRATIONS


def render_integrations_and_models_step(agent: AgentForgeAgent) -> None:
    """Render the integrations and models step."""
    st.markdown("## Select Integrations and Models")
    st.write(
        "This is where we would narrow down which integrations we'll use as well as which model/provider will power it."
    )
    st.write(
        "TBD is whether we should allow for configuration of the LLM being used to generate the agent in addition to the model being used inside the agent we generate"
    )

    # display a bubble for each integration, which you can expand to see the tools available
    selected_integrations = st.multiselect("Select Integrations", SUPPORTED_INTEGRATIONS)
    agent.integrations = selected_integrations
