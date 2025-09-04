import streamlit as st
from any_llm import list_models

from any_forge.state import AgentForgeAgent

DEFAULT_MODEL_ID = "gpt-4.1-mini"


@st.fragment
def render_model_ids(agent: AgentForgeAgent) -> None:
    """Render the models step."""
    st.subheader("Model")
    model_ids = [x.id for x in list_models("openai")]
    if agent.model_id:
        agent_model_id = agent.model_id.split(":")[1] if agent.model_id.split(":")[1] else DEFAULT_MODEL_ID
    else:
        agent_model_id = DEFAULT_MODEL_ID
    model_id = st.selectbox(
        "Select a model", model_ids, index=model_ids.index(agent_model_id), key=f"model_id_{agent.id}"
    )
    agent.model_id = f"openai:{model_id}"
