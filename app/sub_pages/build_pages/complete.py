import streamlit as st

from any_forge.state import AgentStateMachine


def render_complete_step(agent_state: AgentStateMachine):
    st.markdown("## 🎉 Agent Created Successfully!")
    st.success("Your AI agent has been configured and is ready to use.")

    if st.button("🔄 Create Another Agent", key="create_another"):
        agent_state.reset()
        st.rerun()
