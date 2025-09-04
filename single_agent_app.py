import nest_asyncio
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
nest_asyncio.apply()
st.set_page_config(page_title="Any-Forge", page_icon="🔨", layout="wide", initial_sidebar_state="expanded")

from any_forge.state import AgentForgeAgent  # noqa: E402
from app.components import (  # noqa: E402
    render_auth_check,
    render_evaluations,
    render_instructions,
    render_integrations,
    render_model_ids,
    render_run,
    render_task_description,
    render_tools,
)
from app.state import STATE_KEY, StreamlitState  # noqa: E402

if st.session_state.get(STATE_KEY) is None:
    st.session_state[STATE_KEY] = StreamlitState()

if "agent" not in st.session_state:
    st.session_state["agent"] = AgentForgeAgent()

agent = st.session_state["agent"]

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
        st.divider()
        render_run(agent)

        if agent.traces:
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
