from streamlit.testing.v1 import AppTest


def test_instructions_generation(any_forge_app: AppTest) -> None:
    any_forge_app.button("create_new_agent").click().run()
    any_forge_app.button("next_btn").click().run()
    any_forge_app.button("next_btn").click().run()
    any_forge_app.button("next_btn").click().run()
    any_forge_app.button("generate_instructions").click().run(timeout=30)

    current_agent = list(any_forge_app.session_state["agents"].values())[0]  #  noqa: RUF015
    assert current_agent.instructions is not None
