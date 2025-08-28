import streamlit as st

from any_forge.state import AgentForgeAgent


def render_task_description(agent: AgentForgeAgent) -> None:
    """Render the instructions step."""
    task_description = st.text_area("Task Description", height=200, key="task_description")
    if task_description:
        agent.task_description = task_description
