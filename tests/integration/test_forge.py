from streamlit.testing.v1 import AppTest


def test_create_new_agent(any_forge_app: AppTest) -> None:
    n_agents = len(any_forge_app.session_state["agents"])
    any_forge_app.button("create_new_agent").click().run()
    assert len(any_forge_app.session_state["agents"]) == n_agents + 1
