from streamlit.testing.v1 import AppTest


def test_e2e_generation(any_forge_app: AppTest) -> None:
    any_forge_app.button("create_new_agent").click().run()
    any_forge_app.multiselect("integrations").set_value(["GITHUB"]).run()
    any_forge_app.text_area("task_description").set_value("Create an AI agent that can summarize Pull Requests.").run()
    any_forge_app.button("create_agent").click().run(timeout=120)

    current_agent = list(any_forge_app.session_state["agents"].values())[0]  #  noqa: RUF015
    assert current_agent.model_id is not None
    assert current_agent.instructions is not None
    assert current_agent.tools is not None
