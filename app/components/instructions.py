import streamlit as st
from any_agent.frameworks.tinyagent import DEFAULT_SYSTEM_PROMPT

from any_forge.generation.instructions import generate_instructions
from any_forge.state import AgentForgeAgent
from app.state import get_state

SPLIT_BEGINNING = "# Reminders"
FULL_INSTRUCTIONS = f"""
{{base_instructions}}
{{generated_instructions}}
{SPLIT_BEGINNING}
- If a tool call fails with an error, don't try the same call again. Instead, try to understand the error and fix the root cause.
"""


@st.fragment
def render_instructions(agent: AgentForgeAgent) -> None:
    """Render the instructions step."""
    assert agent.task_description is not None
    assert agent.tools is not None

    st.subheader("Instructions")

    placeholder = st.empty()

    if agent.instructions:
        gen_instructions = agent.instructions.split(DEFAULT_SYSTEM_PROMPT)[1].split(SPLIT_BEGINNING)[0].strip()
    else:
        gen_instructions = None

    gen_instructions = get_state().gen_instructions or gen_instructions

    should_regenerate = get_state().should_regenerate_instructions
    if gen_instructions is None or should_regenerate:
        with st.spinner("Generating instructions..."):
            gen_instructions = generate_instructions(agent.task_description, agent.tools)
        get_state().gen_instructions = gen_instructions
        get_state().should_regenerate_instructions = False
    with placeholder.container():
        edited_instructions = st.text_area(
            "Edit Instructions",
            value=gen_instructions,
            height="content",
            key=f"instructions_{agent.id}",
            help="You can edit the generated instructions before finalizing them.",
        )
    get_state().gen_instructions = edited_instructions
    agent.instructions = FULL_INSTRUCTIONS.format(
        base_instructions=DEFAULT_SYSTEM_PROMPT, generated_instructions=edited_instructions
    )
