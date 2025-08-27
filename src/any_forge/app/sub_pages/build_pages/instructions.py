import streamlit as st

from any_forge.generation.instructions import _InstructionGenerator
from any_forge.state import AgentForgeAgent


def render_instructions_step(agent: AgentForgeAgent) -> None:
    """Render the instructions step."""
    st.markdown("## Create Instructions")
    st.write("Here is where we will narrow down and generate the instructions for the agent.")
    task_description = st.text_area("Task Description", height=200, key="task_description")
    if task_description and st.button("Generate Instructions", key="generate_instructions"):
        generator = _InstructionGenerator(task_description)
        with st.spinner("Generating instructions..."):
            st.write_stream(generator.generate())
        agent.instructions = generator.get_full_instructions()
