import streamlit as st

from any_forge.app.components.status_callback import StreamlitStatusCallback
from any_forge.run import run_agent
from any_forge.state import AgentForgeAgent


@st.fragment
def render_run(agent: AgentForgeAgent) -> None:
    """Render the run step."""
    st.subheader("Run the Agent")

    prompt = st.text_area("Prompt", height=200, value=agent.get_prompt())
    agent.prompt = prompt
    if st.button("Run"):
        agent.callbacks = [StreamlitStatusCallback()]
        with st.spinner("Running agent..."):
            trace = run_agent(agent)
        st.download_button(
            label="Download Trace",
            data=trace.model_dump_json(),
            file_name="trace.json",
            mime="application/json",
            icon=":material/download:",
        )
        with st.expander("Trace", expanded=False):
            st.write(trace.spans_to_messages())
