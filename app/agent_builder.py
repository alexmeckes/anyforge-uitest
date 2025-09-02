import streamlit as st

from any_forge.state import AgentForgeAgent
from any_forge.storage import load_agents, save_agents
from app.components import (
    render_auth_check,
    render_instructions,
    render_integrations,
    render_model_ids,
    render_run,
    render_save,
    render_task_description,
    render_tools,
)
from app.state import STATE_KEY, StreamlitState, get_state


def agent_builder_page() -> None:
    """Render the agent builder page."""
    if st.session_state.get(STATE_KEY) is None:
        agents_dict: dict[str, AgentForgeAgent] = dict(load_agents().items())
        st.session_state[STATE_KEY] = StreamlitState(agents=agents_dict)
    state: StreamlitState = get_state()

    with st.sidebar:
        st.title("Agent Selection")
        if st.button("Create New Agent", type="primary", key="create_new_agent"):
            new_agent = AgentForgeAgent()
            state.agents[new_agent.id] = new_agent
            save_agents(state.agents)
            st.success("Created new agent! Starting build process...")
        if not state.agents:
            st.info("No agents found. Click the button above to create a new agent.")
            return
        agent_id = st.selectbox("Select an agent", state.agents.keys())

    if agent := state.agents[agent_id]:
        render_integrations(agent)

        if agent.integrations:
            with st.expander("Authentication Status", expanded=False):
                render_auth_check(agent)

            render_task_description(agent)

            if agent.task_description:
                st.divider()
                render_model_ids(agent)
                st.divider()
                render_tools(agent)
                st.divider()
                render_instructions(agent)

            if agent.model_id and agent.instructions and agent.tools:
                with st.sidebar:
                    render_save(agent)
                st.divider()
                render_run(agent)

                if agent.traces:
                    with st.sidebar:
                        latest_trace = agent.traces[-1]
                        st.download_button(
                            label="Download Latest Trace",
                            data=latest_trace.model_dump_json(),
                            file_name="trace.json",
                            mime="application/json",
                            icon=":material/download:",
                            on_click="ignore",
                            key="download_trace_button",
                        )
                        with st.expander("Latest Trace", expanded=False):
                            st.write(latest_trace.spans_to_messages())
