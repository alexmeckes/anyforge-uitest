import streamlit as st

from any_forge.generation.instructions import generate_instructions
from any_forge.state import AgentForgeAgent


def render_instructions_step(agent: AgentForgeAgent) -> None:
    """Render the instructions step."""
    st.markdown("## Create Instructions")
    st.write("Here is where we will narrow down and generate the instructions for the agent.")
    task_description = st.text_area("Task Description", height=200)
    if st.button("Generate Instructions", key="generate_instructions"):
        with st.spinner("Generating instructions..."):
            instructions = generate_instructions(task_description)
        agent.instructions = instructions
        st.markdown(instructions)
