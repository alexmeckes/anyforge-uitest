import streamlit as st
from any_llm import list_models

from any_forge.state import AgentForgeAgent


@st.fragment
def render_model_ids(agent: AgentForgeAgent) -> None:
    """Render the models step."""
    st.subheader("Model")
    model_ids = [x.id for x in list_models("openai")]
    model_id = st.selectbox("Select a model", model_ids, index=model_ids.index("gpt-4.1-mini"))
    agent.model_id = f"openai:{model_id}"
