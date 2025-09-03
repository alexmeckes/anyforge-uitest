import streamlit as st
from any_agent import AgentTrace
from any_agent.evaluation import AgentJudge
from any_agent.evaluation.schemas import EvaluationOutput

from any_forge.generation.evaluation import generate_evaluation
from any_forge.state import AgentForgeAgent


def _run_single_evaluation(trace: AgentTrace, model_id: str, evaluation: str) -> EvaluationOutput:
    """Run a single evaluation and display results."""
    with st.spinner(f"Running evaluation: {evaluation[:50]}..."):
        agent_judge = AgentJudge(model_id=model_id)
        result = agent_judge.run(trace=trace, question=evaluation)
        final_output = result.final_output
        if not isinstance(final_output, EvaluationOutput):
            err_msg = f"Agent output is not an {EvaluationOutput} instance."
            raise ValueError(err_msg)
        with st.expander(f"Evaluation: {evaluation[:50]}..."):
            st.write(f"Passed: {final_output.passed}")
            st.write(f"Reasoning: {final_output.reasoning}")
        return final_output


@st.fragment
def render_evaluations(agent: AgentForgeAgent) -> None:
    """Render the evaluations step."""
    assert agent.task_description is not None
    assert agent.tools is not None
    assert agent.model_id is not None

    st.subheader("Evaluations")

    current_evaluations = agent.evaluations

    if st.button("+ Autogenerate New Criteria", key="add_evaluation"):
        with st.spinner("Generating new evaluation criteria..."):
            new_evaluation = generate_evaluation(
                task_description=agent.task_description, tools=agent.tools, existing_evaluations=current_evaluations
            )
            updated_evaluations = [*current_evaluations, new_evaluation]
            agent.evaluations = updated_evaluations
            st.rerun()

    if not current_evaluations:
        return

    st.write("**Edit Evaluations:**")

    updated_evaluations = []
    for i, evaluation in enumerate(current_evaluations):
        col1, col2 = st.columns([4, 1])

        with col1:
            edited_evaluation = st.text_area(f"Evaluation {i + 1}", value=evaluation, key=f"evaluation_{i}", height=100)
            if edited_evaluation.strip():
                updated_evaluations.append(edited_evaluation.strip())

        with col2:
            if st.button("🗑️", key=f"delete_evaluation_{i}", help="Delete this evaluation"):
                remaining_evaluations = current_evaluations[:i] + current_evaluations[i + 1 :]
                agent.evaluations = remaining_evaluations
                st.rerun()

    agent.evaluations = updated_evaluations

    if updated_evaluations and agent.traces:
        st.divider()
        if st.button("Run evaluations on latest trace", key="run_evaluations"):
            evaluation_results = []
            for evaluation in updated_evaluations:
                result = _run_single_evaluation(agent.traces[-1], agent.model_id, evaluation)
                evaluation_results.append(result)

            agent.evaluation_results = evaluation_results
