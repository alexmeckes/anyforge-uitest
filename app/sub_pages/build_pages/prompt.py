import streamlit as st

from any_forge.state import AgentStateMachine


def render_instructions_step(agent_state: AgentStateMachine):
    """Render the instructions step."""
    st.markdown("## Create Instructions and Prompt")
    st.write(
        "Here is where we will narrow down and generate the instructions for the agent as well as the initial prompt. Maybe also the output type of the agent if relevant?"
    )
