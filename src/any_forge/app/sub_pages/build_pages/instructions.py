import streamlit as st

from any_forge.generation.instructions import _InstructionGenerator
from any_forge.state import AgentForgeAgent
from any_forge.tools.integrations import SUPPORTED_INTEGRATIONS
from any_forge.tools.tools import get_recommended_tools


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
        with st.spinner("Generating recommended tools..."):
            integrations, tools = get_recommended_tools(task_description, SUPPORTED_INTEGRATIONS)
        st.write(f"We recommend using the following integrations: {integrations}")
        st.write(f"We recommend using the following tools from those integrations: {tools}")
        agent.integrations = integrations
        agent.tools = tools
