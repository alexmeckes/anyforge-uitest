import streamlit as st

from any_forge.state import AgentForgeAgent
from any_forge.storage import save_agents
from app.state import get_state


@st.fragment
def render_complete_agent(agent: AgentForgeAgent) -> None:
    """Render the complete agent button."""
    st.subheader("Complete Agent")
    st.write("Mark this agent as complete to move it to the production environment.")

    if st.button("Mark as Complete", key="complete_btn", type="primary"):
        state = get_state()

        agent.complete = True

        # Move agent from development to completed
        if agent.id in state.development_agents:
            del state.development_agents[agent.id]
        state.completed_agents[agent.id] = agent

        # Save both agent collections
        save_agents(state.development_agents, state.completed_agents)
        st.success("Agent marked as complete and moved to production!")
        st.rerun()


@st.fragment
def render_uncomplete_agent(agent: AgentForgeAgent) -> None:
    """Render the undo complete agent button to move it back to development."""
    st.subheader("Return to Development")
    st.write("Move this agent back to the development environment for further changes.")

    if st.button("Return to Development", key="uncomplete_btn", type="secondary"):
        state = get_state()

        agent.complete = False

        # Move agent from completed to development
        if agent.id in state.completed_agents:
            del state.completed_agents[agent.id]
        state.development_agents[agent.id] = agent

        # Save both agent collections
        save_agents(state.development_agents, state.completed_agents)
        st.success("Agent moved back to development!")
        st.rerun()
