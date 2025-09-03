import streamlit as st

from any_forge.storage import load_agents
from app.components import (
    render_auth_check,
    render_complete_agent,
    render_create_agent,
    render_delete_agent,
    render_evaluations,
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
        development_agents, completed_agents = load_agents()
        st.session_state[STATE_KEY] = StreamlitState(
            development_agents=development_agents, completed_agents=completed_agents
        )
    state: StreamlitState = get_state()

    with st.sidebar:
        render_create_agent()
        if not state.development_agents:
            st.info("No agents found. Click the button above to create a new agent.")
            return
        agent_keys = list(state.development_agents.keys())
        default_index = 0
        if state.selected_agent_id and state.selected_agent_id in agent_keys:
            default_index = agent_keys.index(state.selected_agent_id)

        agent_id = st.selectbox(
            "Select an agent",
            agent_keys,
            index=default_index,
            format_func=lambda x: state.development_agents[x].name or state.development_agents[x].id,
        )

        state.selected_agent_id = agent_id

        if agent_id in state.development_agents:
            render_delete_agent(state.development_agents[agent_id])

    if agent := state.development_agents[agent_id]:
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
                    render_evaluations(agent)

                st.divider()
                render_complete_agent(agent)
