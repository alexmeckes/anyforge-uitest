import streamlit as st

from any_forge.generation.instructions import _InstructionGenerator
from any_forge.state import AgentForgeAgent


@st.fragment
def render_instructions(agent: AgentForgeAgent) -> None:
    """Render the instructions step."""
    assert agent.task_description is not None
    generator = _InstructionGenerator(agent.task_description)
    st.subheader("Instructions")
    with st.spinner("Generating instructions..."):
        st.write_stream(generator.generate())
    agent.instructions = generator.get_full_instructions()
