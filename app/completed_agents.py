import streamlit as st

from any_forge.storage import load_agents
from app.components import (
    render_run,
    render_uncomplete_agent,
)
from app.state import STATE_KEY, StreamlitState, get_state


def completed_agents_page() -> None:
    """Render the completed agents page."""
    if st.session_state.get(STATE_KEY) is None:
        development_agents, completed_agents = load_agents()
        st.session_state[STATE_KEY] = StreamlitState(
            development_agents=development_agents, completed_agents=completed_agents
        )
    state: StreamlitState = get_state()

    st.title("Completed Agents")

    if not state.completed_agents:
        st.info("No completed agents found. Complete an agent from the development environment to see it here.")
        return

    agent_keys = list(state.completed_agents.keys())
    default_index = 0
    if state.selected_agent_id and state.selected_agent_id in agent_keys:
        default_index = agent_keys.index(state.selected_agent_id)

    agent_id = st.selectbox(
        "Select a completed agent",
        agent_keys,
        index=default_index,
        format_func=lambda x: state.completed_agents[x].name or state.completed_agents[x].id,
    )
    state.selected_agent_id = agent_id

    if agent := state.completed_agents[agent_id]:
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader(f"Agent: {agent.name or agent.id}")
            if agent.task_description:
                st.write("**Task Description:**")
                st.write(agent.task_description)

            if agent.instructions:
                with st.expander("Instructions", expanded=False):
                    st.write(agent.instructions)

            if agent.tools:
                with st.expander("Available Tools", expanded=False):
                    for tool in agent.tools:
                        st.write(f"- {tool}")

        with col2:
            st.write("**Agent Info**")
            st.write(f"Model: {agent.model_id}")
            st.write(f"Integrations: {len(agent.integrations)}")
            st.write(f"Tools: {len(agent.tools)}")
            st.write(f"Runs: {len(agent.traces)}")

        st.divider()

        render_run(agent)

        if agent.traces:
            with st.expander("Latest Trace", expanded=False):
                latest_trace = agent.traces[-1]
                st.write(latest_trace.spans_to_messages())

        st.divider()

        render_uncomplete_agent(agent)
