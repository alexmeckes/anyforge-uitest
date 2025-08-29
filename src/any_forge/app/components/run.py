import streamlit as st

from any_forge.app.components.status_callback import StreamlitStatusCallback
from any_forge.run import run_agent
from any_forge.state import AgentForgeAgent


@st.fragment
def render_run(agent: AgentForgeAgent) -> None:
    """Render the run step."""
    st.subheader("Run the Agent")

    prompt = st.text_area("Prompt", height=200, value=agent.get_prompt(), key="prompt")
    agent.prompt = prompt

    if st.button("Run", key="run_button"):
        agent.callbacks = [StreamlitStatusCallback()]
        with st.spinner("Running agent..."):
            trace = run_agent(agent)
            agent.traces.append(trace)

    if agent.traces:
        latest_trace = agent.traces[-1]
        st.download_button(
            label="Download Trace",
            data=latest_trace.model_dump_json(),
            file_name="trace.json",
            mime="application/json",
            icon=":material/download:",
            on_click="ignore",
            key="download_trace_button",
        )
        with st.expander("Trace", expanded=False):
            st.write(latest_trace.spans_to_messages())
