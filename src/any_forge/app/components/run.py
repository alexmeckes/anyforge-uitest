import streamlit as st

from any_forge.app.components.status_callback import StreamlitStatusCallback
from any_forge.run import run_agent
from any_forge.state import AgentForgeAgent


@st.fragment
def render_run(agent: AgentForgeAgent) -> None:
    """Render the run step."""
    st.subheader("Run the Agent")

    if st.button("Clear Conversation", type="secondary", key="clear_conversation"):
        st.session_state.messages = []

    conversation = st.container()
    if "messages" in st.session_state:
        for message in st.session_state.messages:
            conversation.chat_message(message["role"], avatar=message.get("avatar", None)).write(message["content"])
    else:
        st.session_state.messages = []

    if prompt := st.chat_input():
        conversation.chat_message("user").write(prompt)
        if st.session_state.messages:
            agent.prompt = f"Conversation history:\n{st.session_state.messages}. New message: {prompt}"
        else:
            agent.prompt = prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        agent.callbacks = [StreamlitStatusCallback(conversation)]  # type: ignore[no-untyped-call]
        trace = run_agent(agent)
        agent.traces.append(trace)

        if trace:
            st.rerun()
