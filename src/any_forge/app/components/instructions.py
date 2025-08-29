import streamlit as st

from any_forge.generation.instructions import _InstructionGenerator
from any_forge.state import AgentForgeAgent


@st.fragment
def render_instructions(agent: AgentForgeAgent) -> None:
    """Render the instructions step."""
    assert agent.task_description is not None
    st.subheader("Instructions")

    placeholder = st.empty()

    gen_instructions = st.session_state.get("gen_instructions", None)

    generator = _InstructionGenerator(agent.task_description, agent.tools)
    if gen_instructions is None:
        with st.spinner("Generating instructions..."):
            # Stream the content to the placeholder
            with placeholder.container():
                st.write_stream(generator.generate())
        # Store the generated instructions
        gen_instructions = generator.general_instructions
        st.session_state["gen_instructions"] = gen_instructions

    with placeholder.container():
        edited_instructions = st.text_area(
            "Edit Instructions",
            value=gen_instructions,
            height="content",
            key=f"instructions_{agent.id}",
            help="You can edit the generated instructions before finalizing them.",
        )

    generator.general_instructions = edited_instructions
    agent.instructions = generator.get_full_instructions()
