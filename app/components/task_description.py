import streamlit as st

from any_forge.state import AgentForgeAgent
from app.state import get_state


def render_task_description(agent: AgentForgeAgent) -> None:
    """Render the instructions step."""
    if agent.task_description:
        existing_task_description = agent.task_description
    else:
        existing_task_description = None

    descr = get_state().task_description or existing_task_description
    task_description = st.text_area("Task Description", height=200, key="task_description", value=descr)
    if task_description and task_description != agent.task_description:
        agent.task_description = task_description
        get_state().should_regenerate_instructions = True
        get_state().should_regenerate_tools = True
