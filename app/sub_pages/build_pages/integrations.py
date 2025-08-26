import streamlit as st

from any_forge.state import AgentStateMachine


def render_integrations_and_models_step(agent_state: AgentStateMachine):
    st.markdown("## Select Integrations and Models")
    st.write(
        "This is where we would narrow down which integrations we'll use as well as which model/provider will power it."
    )
    st.write(
        "TBD is whether we should allow for configuration of the LLM being used to generate the agent in addition to the model being used inside the agent we generate"
    )
