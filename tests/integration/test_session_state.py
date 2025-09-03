from streamlit.testing.v1 import AppTest

from app.state import STATE_KEY


def test_create_new_agent(any_forge_app: AppTest) -> None:
    n_agents = len(any_forge_app.session_state[STATE_KEY].agents)
    any_forge_app.button(key="create_new_agent").click().run()
    assert len(any_forge_app.session_state[STATE_KEY].agents) == n_agents + 1
