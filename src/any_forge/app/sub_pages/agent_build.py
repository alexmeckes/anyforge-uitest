import streamlit as st

from any_forge.app.sub_pages.build_pages import (
    render_complete_step,
    render_instructions_step,
    render_integrations_and_models_step,
    render_review_step,
    render_welcome_step,
)
from any_forge.state import AgentCreationState, AgentForgeAgent
from any_forge.storage.storage import load_agents, save_agents


def agent_builder_page() -> None:
    """Render the agent builder page."""
    if st.session_state.get("agents") is None:
        st.session_state["agents"] = dict(load_agents().items())

    agents = st.session_state["agents"]

    st.write(f"Found {len(agents)} agents")
    if st.button("Create New Agent", type="primary", key="create_new_agent"):
        new_agent = AgentForgeAgent()
        st.session_state["agents"][new_agent.id] = new_agent
        save_agents(st.session_state["agents"])
        st.success("Created new agent! Starting build process...")
    else:
        st.info("Click the button above to create a new agent.")
    if not agents:
        st.info("No agents found. Click the button above to create a new agent.")
        return

    agent = st.selectbox("Select an agent", agents.keys())
    if agent:
        agent_id = agent
        agent = agents[agent_id]
        agent_state = agent.state_machine

        if agent_state.state == AgentCreationState.INIT:
            render_welcome_step(agent)

        elif agent_state.state in [AgentCreationState.SELECT_INTEGRATIONS, AgentCreationState.SELECT_MODEL]:
            render_integrations_and_models_step(agent)

        elif agent_state.state == AgentCreationState.CREATE_PROMPT:
            render_instructions_step(agent)

        elif agent_state.state == AgentCreationState.REVIEW:
            render_review_step(agent)

        elif agent_state.state == AgentCreationState.COMPLETE:
            render_complete_step(agent)

        else:
            err_msg = f"Unexpected state: {agent_state.state}"
            raise ValueError(err_msg)

        st.divider()

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("Save", key="save_btn"):
                save_agents(st.session_state["agents"])
                st.success("Agent saved!")

            if agent_state.state != AgentCreationState.INIT:
                if st.button("← Previous", key="prev_btn"):
                    agent_state.previous_state()
                    st.rerun()

        with col2:
            if st.button("🔄 Reset", key="reset_btn", help="Start over"):
                agent_state.reset()
                st.rerun()

        with col3:
            can_advance = agent_state.can_advance()
            if st.button("Next →", key="next_btn", disabled=not can_advance):
                if can_advance:
                    agent_state.next_state()
                    st.rerun()
