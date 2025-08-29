from streamlit.testing.v1 import AppTest

from any_forge.state import AgentForgeAgent


def _get_agent(any_forge_app: AppTest) -> AgentForgeAgent:
    agents = list(any_forge_app.session_state["agents"].values())
    assert len(agents) == 1
    agent = agents[0]
    assert agent is not None
    assert isinstance(agent, AgentForgeAgent)
    return agent


def test_e2e_generation(any_forge_app: AppTest) -> None:
    any_forge_app.button(key="create_new_agent").click().run()
    any_forge_app.multiselect("integrations").set_value(["GITHUB"]).run()
    assert _get_agent(any_forge_app).integrations is not None
    any_forge_app.text_area(key="task_description").set_value(
        "Create an AI agent that can summarize Pull Requests."
    ).run()
    assert _get_agent(any_forge_app).task_description is not None
    any_forge_app.button(key="create_agent").click().run(timeout=120)

    current_agent = _get_agent(any_forge_app)
    assert current_agent.model_id is not None
    assert current_agent.instructions is not None
    assert current_agent.tools is not None

    any_forge_app.text_area(key="prompt").set_value("Find my most recent pull request").run()
    assert _get_agent(any_forge_app).prompt is not None
    any_forge_app.button(key="run_button").click().run(timeout=120)
    assert _get_agent(any_forge_app).traces is not None
    assert len(_get_agent(any_forge_app).traces) == 1
    assert _get_agent(any_forge_app).traces[0].final_output is not None
