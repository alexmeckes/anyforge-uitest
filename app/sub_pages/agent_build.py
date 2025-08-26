import streamlit as st
from models.state import initialize_state_machine
from sub_pages.build import (
    render_complete_step,
    render_instructions_step,
    render_integrations_and_models_step,
    render_review_step,
    render_welcome_step,
)

from any_forge.state import AgentCreationState

# Right now, we just have a single state machine to track a single agent. As we expand this I imagine each agent in the forge will have it's own state machine, that way we can track how each agent is doing
agent_state = initialize_state_machine()


def agent_builder_page() -> None:
    """Render the agent builder page."""
    st.title(f"🤖 Agent Builder State: {agent_state.state}")

    if agent_state.state == AgentCreationState.INIT:
        render_welcome_step(agent_state)

    elif agent_state.state in [AgentCreationState.SELECT_INTEGRATIONS, AgentCreationState.SELECT_MODEL]:
        render_integrations_and_models_step(agent_state)

    elif agent_state.state == AgentCreationState.CREATE_PROMPT:
        render_instructions_step(agent_state)

    elif agent_state.state == AgentCreationState.REVIEW:
        render_review_step(agent_state)

    elif agent_state.state == AgentCreationState.COMPLETE:
        render_complete_step(agent_state)

    else:
        err_msg = f"Unexpected state: {agent_state.state}"
        raise ValueError(err_msg)

    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if agent_state.state != AgentCreationState.INIT:
            if st.button("← Previous", key="prev_btn"):
                agent_state.previous_state()
                st.rerun()

    with col2:
        if st.button("🔄 Reset", key="reset_btn", help="Start over"):
            agent_state.reset()
            st.rerun()

    with col3:
        can_advance = agent_state.can_advance()
        if st.button("Next →", key="next_btn", disabled=not can_advance):
            if can_advance:
                agent_state.next_state()
                st.rerun()
