# mypy: disable-error-code="no-untyped-def,operator,misc,arg-type,no-any-return"
import inspect
import json
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from any_forge.integrations import create_tool_callable


@pytest.fixture
def slack_tools_spec() -> list[dict[str, Any]]:
    """Load the Slack tools specification from JSON file."""
    spec_file = Path(__file__).parent.parent / "assets" / "slack_tools_spec.json"
    with spec_file.open() as f:
        return json.load(f)


@pytest.fixture
def mock_composio() -> Generator[Mock, None, None]:
    """Mock Composio instance for testing."""
    with (
        patch("any_forge.integrations.composio") as mock_composio,
        patch("any_forge.integrations.user_id", "test_user"),
    ):
        mock_composio.tools.execute.return_value = {"successful": True, "data": {"result": "success"}}
        yield mock_composio


def test_creates_callable_from_slack_send_message_spec(slack_tools_spec):
    """Test creating callable from SLACK_SEND_MESSAGE spec."""
    send_message_spec = next(
        tool["function"] for tool in slack_tools_spec if tool["function"]["name"] == "SLACK_SEND_MESSAGE"
    )

    callable_func = create_tool_callable(send_message_spec)

    assert callable(callable_func)
    assert callable_func.__name__ == "SLACK_SEND_MESSAGE"
    assert "Posts a message to a slack channel" in callable_func.__doc__


def test_function_signature_has_correct_parameters(slack_tools_spec):
    """Test that generated function has correct parameter signature."""
    send_message_spec = next(
        tool["function"] for tool in slack_tools_spec if tool["function"]["name"] == "SLACK_SEND_MESSAGE"
    )

    callable_func = create_tool_callable(send_message_spec)
    sig = inspect.signature(callable_func)

    # Check required parameter
    assert "channel" in sig.parameters
    assert sig.parameters["channel"].default == inspect.Parameter.empty
    assert sig.parameters["channel"].annotation is str

    # Check optional parameters
    assert "as_user" in sig.parameters
    assert sig.parameters["as_user"].default is None
    assert sig.parameters["as_user"].annotation == bool | None

    assert "markdown_text" in sig.parameters
    assert sig.parameters["markdown_text"].default is None
    assert sig.parameters["markdown_text"].annotation == str | None

    # Check return annotation
    assert sig.return_annotation is dict


def test_parameter_type_conversion(slack_tools_spec):
    """Test that JSON schema types are correctly converted to Python types."""
    find_users_spec = next(
        tool["function"] for tool in slack_tools_spec if tool["function"]["name"] == "SLACK_FIND_USERS"
    )

    callable_func = create_tool_callable(find_users_spec)
    sig = inspect.signature(callable_func)

    # String parameter
    assert sig.parameters["search_query"].annotation is str

    # Boolean parameter
    assert sig.parameters["exact_match"].annotation == bool | None

    # Integer parameter
    assert sig.parameters["limit"].annotation == int | None


def test_required_vs_optional_parameters(slack_tools_spec):
    """Test that required and optional parameters are handled correctly."""
    find_channels_spec = next(
        tool["function"] for tool in slack_tools_spec if tool["function"]["name"] == "SLACK_FIND_CHANNELS"
    )

    callable_func = create_tool_callable(find_channels_spec)
    sig = inspect.signature(callable_func)

    # Required parameter should not have default value
    search_query_param = sig.parameters["search_query"]
    assert search_query_param.default == inspect.Parameter.empty
    assert search_query_param.annotation is str

    # Optional parameters should have None default
    exact_match_param = sig.parameters["exact_match"]
    assert exact_match_param.default is None
    assert exact_match_param.annotation == bool | None


def test_function_execution_with_valid_args(slack_tools_spec, mock_composio):
    """Test that generated function executes correctly with valid arguments."""
    send_message_spec = next(
        tool["function"] for tool in slack_tools_spec if tool["function"]["name"] == "SLACK_SEND_MESSAGE"
    )

    callable_func = create_tool_callable(send_message_spec)

    result = callable_func(channel="general", markdown_text="Hello World")

    assert result == {"result": "success"}
    mock_composio.tools.execute.assert_called_once_with(
        "SLACK_SEND_MESSAGE", user_id="test_user", arguments={"channel": "general", "markdown_text": "Hello World"}
    )


def test_function_execution_with_only_required_args(slack_tools_spec, mock_composio):
    """Test function execution with only required arguments."""
    find_users_spec = next(
        tool["function"] for tool in slack_tools_spec if tool["function"]["name"] == "SLACK_FIND_USERS"
    )

    callable_func = create_tool_callable(find_users_spec)

    result = callable_func(search_query="john.doe@company.com")

    assert result == {"result": "success"}
    mock_composio.tools.execute.assert_called_once_with(
        "SLACK_FIND_USERS", user_id="test_user", arguments={"search_query": "john.doe@company.com"}
    )


def test_function_execution_handles_composio_error(slack_tools_spec, mock_composio):
    """Test that function raises error when Composio execution fails."""
    mock_composio.tools.execute.return_value = {"successful": False, "error": "Channel not found"}

    send_message_spec = next(
        tool["function"] for tool in slack_tools_spec if tool["function"]["name"] == "SLACK_SEND_MESSAGE"
    )

    callable_func = create_tool_callable(send_message_spec)

    with pytest.raises(ValueError, match="Channel not found"):
        callable_func(channel="nonexistent")


def test_all_parameters_are_keyword_only(slack_tools_spec, mock_composio):
    """Test that all generated function parameters are keyword-only."""
    send_message_spec = next(
        tool["function"] for tool in slack_tools_spec if tool["function"]["name"] == "SLACK_SEND_MESSAGE"
    )

    callable_func = create_tool_callable(send_message_spec)
    sig = inspect.signature(callable_func)

    for param in sig.parameters.values():
        assert param.kind == inspect.Parameter.KEYWORD_ONLY


def test_raises_error_when_composio_not_configured(slack_tools_spec):
    """Test that function raises error when Composio is not configured."""
    with patch("any_forge.integrations.composio", None), patch("any_forge.integrations.user_id", None):
        send_message_spec = next(
            tool["function"] for tool in slack_tools_spec if tool["function"]["name"] == "SLACK_SEND_MESSAGE"
        )

        callable_func = create_tool_callable(send_message_spec)

        with pytest.raises(ValueError, match="COMPOSIO_API_KEY and COMPOSIO_USER_ID"):
            callable_func(channel="test")


def test_raises_error_for_invalid_spec():
    """Test that function raises appropriate errors for invalid specs."""
    # Missing name
    with pytest.raises(ValueError, match="Name is required"):
        create_tool_callable({"description": "test", "parameters": {}})

    # Missing description
    with pytest.raises(ValueError, match="Description is required"):
        create_tool_callable({"name": "test", "parameters": {}})

    # Missing parameters
    with pytest.raises(ValueError, match="Parameters are required"):
        create_tool_callable({"name": "test", "description": "test"})


def test_handles_unknown_parameter_types():
    """Test that unknown parameter types default to string."""
    spec = {
        "name": "TEST_FUNCTION",
        "description": "Test function",
        "parameters": {
            "type": "object",
            "properties": {
                "unknown_type_param": {"type": "unknown_type", "description": "Parameter with unknown type"}
            },
            "required": ["unknown_type_param"],
        },
    }

    callable_func = create_tool_callable(spec)
    sig = inspect.signature(callable_func)

    assert sig.parameters["unknown_type_param"].annotation is str
