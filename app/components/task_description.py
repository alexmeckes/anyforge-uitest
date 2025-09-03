import streamlit as st

from any_forge.state import AgentForgeAgent
from app.state import get_state


def render_task_description(agent: AgentForgeAgent) -> None:
    """Render the instructions step."""
    # Use agent-specific key to avoid state conflicts between different agents
    task_description_key = f"task_description_{agent.id}"

    # Initialize the text area with the agent's current task description
    current_value = agent.task_description or ""

    task_description = st.text_area("Task Description", height=200, key=task_description_key, value=current_value)

    if task_description != agent.task_description:
        agent.task_description = task_description
        get_state().should_regenerate_instructions = True
        get_state().should_regenerate_tools = True
