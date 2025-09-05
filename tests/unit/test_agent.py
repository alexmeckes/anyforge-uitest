from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from any_agent import AgentTrace

from any_forge.run import run_agent_async
from any_forge.state import AgentForgeAgent


@pytest.mark.asyncio
@patch("any_forge.integrations.Composio")
@patch("any_forge.run.AnyAgent.create_async")
async def test_run_agent(mock_create_async: AsyncMock, mock_composio: AsyncMock) -> None:
    mock_agent = AsyncMock()
    mock_trace = MagicMock(spec=AgentTrace)
    mock_agent.run_async.return_value = mock_trace
    mock_create_async.return_value = mock_agent

    agent = AgentForgeAgent()
    agent.model_id = "openai:gpt-5-nano"
    agent.instructions = "You are a helpful assistant"
    agent.tools = ["SLACK_SEND_MESSAGE"]

    trace = await run_agent_async(forge_agent=agent)

    assert trace == mock_trace
    mock_create_async.assert_called_once()
    mock_agent.run_async.assert_called_once()


@pytest.mark.asyncio
@patch("any_forge.integrations.Composio")
@patch("any_forge.run.AnyAgent.create_async")
async def test_create_agent_no_tools(mock_create_async: AsyncMock, mock_composio: AsyncMock) -> None:
    mock_agent = AsyncMock()
    mock_trace = MagicMock(spec=AgentTrace)
    mock_agent.run_async.return_value = mock_trace
    mock_create_async.return_value = mock_agent

    agent = AgentForgeAgent()
    agent.model_id = "openai:gpt-5-nano"
    agent.instructions = "You are a helpful assistant"

    with pytest.raises(ValueError, match="tools is required"):
        agent.get_agent_config()

    agent.tools = ["SLACK_SEND_MESSAGE"]

    agent.get_agent_config()
