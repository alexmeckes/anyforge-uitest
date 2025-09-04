from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from any_forge.state import AgentForgeAgent
from app.state import STATE_KEY


def test_create_new_agent_with_name(any_forge_app: AppTest) -> None:
    """Test creating a new agent with a custom name."""

    any_forge_app.text_input(key="create_agent_form_agent_name").set_value("Test Agent").run()
    any_forge_app.button(key="create_new_agent").click().run()

    state = any_forge_app.session_state[STATE_KEY]
    assert len(state.development_agents) == 1

    new_agent = list(state.development_agents.values())[-1]
    assert new_agent.name == "Test Agent"
    assert state.selected_agent_id == new_agent.id
    assert isinstance(new_agent, AgentForgeAgent)


def test_create_new_agent_without_name(any_forge_app: AppTest) -> None:
    """Test creating a new agent without providing a name (auto-generated)."""

    with patch("app.components.create.datetime") as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = "2024-01-01_12:00:00"

        any_forge_app.button(key="create_new_agent").click().run()

    state = any_forge_app.session_state[STATE_KEY]
    assert len(state.development_agents) == 1

    new_agent = list(state.development_agents.values())[-1]
    assert new_agent.name == "2024-01-01_12:00:00"
    assert state.selected_agent_id == new_agent.id


def test_delete_agent_workflow(any_forge_app: AppTest) -> None:
    """Test the complete agent deletion workflow including confirmation."""

    any_forge_app.text_input(key="create_agent_form_agent_name").set_value("Agent to Delete").run()
    any_forge_app.button(key="create_new_agent").click().run()

    initial_state = any_forge_app.session_state[STATE_KEY]
    agent_to_delete = list(initial_state.development_agents.values())[-1]

    any_forge_app.button(key="delete_btn").click().run()

    state_after_delete_click = any_forge_app.session_state[STATE_KEY]
    assert state_after_delete_click.delete_confirmation is True

    any_forge_app.button(key="confirm_delete").click().run()

    # Verify agent is deleted
    final_state = any_forge_app.session_state[STATE_KEY]
    assert len(final_state.development_agents) == 0
    assert agent_to_delete.id not in final_state.development_agents
    assert final_state.selected_agent_id is None
    assert final_state.delete_confirmation is False


def test_create_new_agent_resets_messages(any_forge_app: AppTest) -> None:
    """Test that creating a new agent resets the conversation messages."""

    state = any_forge_app.session_state[STATE_KEY]
    state.messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How are you?"},
    ]

    assert len(state.messages) == 3

    any_forge_app.text_input(key="create_agent_form_agent_name").set_value("Test Agent").run()
    any_forge_app.button(key="create_new_agent").click().run()

    updated_state = any_forge_app.session_state[STATE_KEY]
    assert len(updated_state.messages) == 0
    assert updated_state.messages == []
