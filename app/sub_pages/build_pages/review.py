import streamlit as st

from any_forge.state import AgentStateMachine


def render_review_step(agent_state: AgentStateMachine):
    st.markdown("## Review Configuration")
    st.write("This is where you would run and review how the agent is doing before you finalize")
