import streamlit as st

from any_forge.state import AgentForgeAgent
from any_forge.storage import save_agents
from app.state import STATE_KEY, get_state


@st.fragment
def render_delete_agent(agent: AgentForgeAgent) -> None:
    """Render the delete agent component with confirmation."""
    state = get_state()

    if st.button("🗑️ Delete Agent", key="delete_btn", type="secondary", help="Delete this agent permanently"):
        state.delete_confirmation = True
        st.session_state[STATE_KEY] = state

    if state.delete_confirmation:
        st.warning(f"⚠️ Are you sure you want to delete agent '{agent.name or agent.id}'?")
        st.write("This action cannot be undone.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Yes, Delete", key="confirm_delete", type="primary"):
                if agent.id in state.agents:
                    del state.agents[agent.id]
                    if state.selected_agent_id == agent.id:
                        state.selected_agent_id = None
                    save_agents(state.agents)
                    st.success(f"Agent '{agent.name or agent.id}' has been deleted!")
                    state.delete_confirmation = False
                    st.session_state[STATE_KEY] = state
                    st.rerun()

        with col2:
            if st.button("❌ Cancel", key="cancel_delete"):
                state.delete_confirmation = False
                st.session_state[STATE_KEY] = state
                st.rerun()
