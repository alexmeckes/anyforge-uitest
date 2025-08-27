import streamlit as st

from any_forge.app.components.streamlit_callback import StreamlitStatusCallback
from any_forge.run import run_agent
from any_forge.state import AgentForgeAgent


def render_review_step(agent: AgentForgeAgent) -> None:
    """Render the review step."""
    st.markdown("## Review Configuration")
    st.write("This is where you would run and review how the agent is doing before you finalize")
    agent.callbacks = [StreamlitStatusCallback()]
    agent.model_id = "openai:gpt-5"
    st.write(f"Using hardcoded model_id and callbacks: {agent.model_id} and {agent.callbacks}")

    st.write(agent.get_agent_config())

    prompt = st.text_area("Prompt", height=200, value=agent.get_prompt())
    agent.prompt = prompt
    if st.button("Run"):
        with st.spinner("Running agent..."):
            out = run_agent(agent)
        with st.expander("Trace", expanded=False):
            st.write(out.spans_to_messages())
    agent.callbacks = []
