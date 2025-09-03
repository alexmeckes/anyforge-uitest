from datetime import datetime

import streamlit as st

from any_forge.state import AgentForgeAgent
from any_forge.storage import save_agents
from app.state import get_state


@st.fragment
def render_create_agent() -> None:
    """Render the create new agent component."""
    state = get_state()

    st.title("Agent Selection")

    with st.form("create_agent_form", clear_on_submit=True):
        st.write("**Create New Agent**")
        agent_name = st.text_input(
            "Agent Name (optional)",
            placeholder="Leave blank for auto-generated name",
            help="If left blank, a timestamp-based name will be generated",
            key="create_agent_form_agent_name",
        )

        submitted = st.form_submit_button("Create New Agent", type="primary", key="create_new_agent")

        if submitted:
            new_agent = AgentForgeAgent()
            if agent_name.strip():
                new_agent.name = agent_name.strip()
            else:
                new_agent.name = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

            state.development_agents[new_agent.id] = new_agent
            state.selected_agent_id = new_agent.id
            save_agents(state.development_agents, state.completed_agents)
            st.rerun()  # this makes it so that the page refreshes and picks up the new agent as being an option.
