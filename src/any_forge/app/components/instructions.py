import streamlit as st
from any_agent.frameworks.tinyagent import DEFAULT_SYSTEM_PROMPT

from any_forge.generation.instructions import generate_instructions
from any_forge.state import AgentForgeAgent

FULL_INSTRUCTIONS = """
{base_instructions}
{generated_instructions}
# Reminders
- If a tool call fails with an error, don't try the same call again. Instead, try to understand the error and fix the root cause.
"""


@st.fragment
def render_instructions(agent: AgentForgeAgent) -> None:
    """Render the instructions step."""
    assert agent.task_description is not None
    assert agent.tools is not None

    st.subheader("Instructions")

    placeholder = st.empty()

    gen_instructions = st.session_state.get("gen_instructions", None)

    if gen_instructions is None:
        with st.spinner("Generating instructions..."):
            gen_instructions = generate_instructions(agent.task_description, agent.tools)
        st.session_state["gen_instructions"] = gen_instructions

    with placeholder.container():
        edited_instructions = st.text_area(
            "Edit Instructions",
            value=gen_instructions,
            height="content",
            key=f"instructions_{agent.id}",
            help="You can edit the generated instructions before finalizing them.",
        )

    agent.instructions = FULL_INSTRUCTIONS.format(
        base_instructions=DEFAULT_SYSTEM_PROMPT, generated_instructions=edited_instructions
    )
