import streamlit as st

from any_forge.app.sub_pages.build_pages import (
    render_instructions,
    render_integrations,
    render_model_ids,
    render_run,
    render_save,
    render_task_description,
    render_tools,
)
from any_forge.state import AgentForgeAgent
from any_forge.storage.storage import load_agents, save_agents


def agent_builder_page() -> None:
    """Render the agent builder page."""
    if st.session_state.get("agents") is None:
        st.session_state["agents"] = dict(load_agents().items())

    agents: dict[str, AgentForgeAgent] = st.session_state["agents"]

    with st.sidebar:
        st.title("Agent Selection")
        if st.button("Create New Agent", type="primary", key="create_new_agent"):
            new_agent = AgentForgeAgent()
            st.session_state["agents"][new_agent.id] = new_agent
            save_agents(st.session_state["agents"])
            st.success("Created new agent! Starting build process...")
        if not agents:
            st.info("No agents found. Click the button above to create a new agent.")
            return
        agent_id = st.selectbox("Select an agent", agents.keys())

    if agent := agents[agent_id]:
        render_integrations(agent)

        if agent.integrations:
            render_task_description(agent)

            if agent.task_description:
                if st.button("Create Agent", key="create_agent"):
                    st.divider()
                    col1, col2, col3 = st.columns([1, 1, 1])

                    with col1:
                        render_model_ids(agent)

                    with col2:
                        render_tools(agent)

                    with col3:
                        render_instructions(agent)

                    if agent.model_id and agent.instructions and agent.tools:
                        with st.sidebar:
                            render_save(agent)
                        render_run(agent)
