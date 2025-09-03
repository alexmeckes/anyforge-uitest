from streamlit.testing.v1 import AppTest

from any_forge.state import AgentForgeAgent
from app.state import STATE_KEY


def _get_agent(any_forge_app: AppTest) -> AgentForgeAgent:
    agents = list(any_forge_app.session_state[STATE_KEY].agents.values())
    assert len(agents) == 1
    agent = agents[0]
    assert agent is not None
    assert isinstance(agent, AgentForgeAgent)
    return agent


def test_e2e_generation(any_forge_app: AppTest) -> None:
    any_forge_app.button(key="create_new_agent").click().run()
    any_forge_app.multiselect("integrations").set_value(["GITHUB"]).run()
    assert _get_agent(any_forge_app).integrations is not None

    # Get the agent to access its ID for the dynamic key
    agent = _get_agent(any_forge_app)
    task_description_key = f"task_description_{agent.id}"

    any_forge_app.text_area(key=task_description_key).set_value(
        "Create an AI agent that can summarize Pull Requests."
    ).run(timeout=120)

    current_agent = _get_agent(any_forge_app)
    assert current_agent.model_id is not None
    assert current_agent.instructions is not None
    assert current_agent.tools is not None

    any_forge_app.chat_input(key="prompt_input").set_value("Find my most recent pull request").run(timeout=120)
    assert _get_agent(any_forge_app).traces is not None
    assert len(_get_agent(any_forge_app).traces) == 1
    assert _get_agent(any_forge_app).traces[0].final_output is not None

    # Test evaluation generation
    any_forge_app.button(key="add_evaluation").click().run(timeout=60)
    current_agent = _get_agent(any_forge_app)
    assert current_agent.evaluations is not None
    assert len(current_agent.evaluations) == 1
    assert isinstance(current_agent.evaluations[0], str)
    assert len(current_agent.evaluations[0].strip()) > 0

    # Test running evaluations on the latest trace
    any_forge_app.button(key="run_evaluations").click().run(timeout=60)
    current_agent = _get_agent(any_forge_app)
    assert len(current_agent.traces) == 1
    assert current_agent.evaluation_results is not None
    assert len(current_agent.evaluation_results) == 1
    assert hasattr(current_agent.evaluation_results[0], "passed")
    assert hasattr(current_agent.evaluation_results[0], "reasoning")
