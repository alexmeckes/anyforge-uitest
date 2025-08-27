from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from any_agent import AgentTrace

from any_forge.run import run_agent_async
from any_forge.state import AgentCreationState, AgentForgeAgent


def test_get_agent_config_success() -> None:
    """Test get_agent_config succeeds in runnable states."""
    agent = AgentForgeAgent()
    agent.model_id = "openai:gpt-5-nano"

    agent.state_machine.state = AgentCreationState.REVIEW
    agent.get_agent_config()

    agent.state_machine.state = AgentCreationState.COMPLETE
    agent.get_agent_config()


def test_get_agent_config_failure_model_id() -> None:
    """Test get_agent_config raises ValueError if model_id is not set."""
    agent = AgentForgeAgent()
    agent.state_machine.state = AgentCreationState.REVIEW
    with pytest.raises(ValueError, match="model_id is required"):
        agent.get_agent_config()


def test_get_agent_config_failure() -> None:
    """Test get_agent_config raises ValueError in non-runnable states."""
    agent = AgentForgeAgent()
    agent.model_id = "openai:gpt-5-nano"
    invalid_states = [
        AgentCreationState.INIT,
        AgentCreationState.SELECT_INTEGRATIONS,
        AgentCreationState.SELECT_MODEL,
        AgentCreationState.CREATE_PROMPT,
    ]

    for state in invalid_states:
        agent.state_machine.state = state
        with pytest.raises(ValueError, match=f"Agent cannot create config: state is {state}"):
            agent.get_agent_config()


def test_get_prompt_success() -> None:
    """Test get_prompt succeeds in runnable states."""
    agent = AgentForgeAgent()

    agent.state_machine.state = AgentCreationState.REVIEW
    agent.get_prompt()

    agent.state_machine.state = AgentCreationState.COMPLETE
    agent.get_prompt()


def test_get_prompt_failure() -> None:
    """Test get_prompt raises ValueError in non-runnable states."""
    agent = AgentForgeAgent()
    invalid_states = [
        AgentCreationState.INIT,
        AgentCreationState.SELECT_INTEGRATIONS,
        AgentCreationState.SELECT_MODEL,
        AgentCreationState.CREATE_PROMPT,
    ]

    for state in invalid_states:
        agent.state_machine.state = state
        with pytest.raises(ValueError, match=f"Agent cannot get prompt: state is {state}"):
            agent.get_prompt()


@pytest.mark.asyncio
@patch("any_forge.run.AnyAgent.create_async")
async def test_run_agent(mock_create_async: AsyncMock) -> None:
    mock_agent = AsyncMock()
    mock_trace = MagicMock(spec=AgentTrace)
    mock_agent.run_async.return_value = mock_trace
    mock_create_async.return_value = mock_agent

    agent = AgentForgeAgent()
    agent.state_machine.state = AgentCreationState.COMPLETE
    agent.model_id = "openai:gpt-5-nano"

    trace = await run_agent_async(forge_agent=agent)

    assert trace == mock_trace
    mock_create_async.assert_called_once()
    mock_agent.run_async.assert_called_once()
