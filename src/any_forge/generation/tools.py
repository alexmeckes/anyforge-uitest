from typing import Any

from any_llm import acompletion
from any_llm.utils.aio import run_async_in_sync
from pydantic import BaseModel

from any_forge.integrations import Integration, get_integrations

SELECTION_MODEL = "openai:gpt-5-nano"


class IntegrationSelection(BaseModel):
    """Integration selection."""

    integrations: list[str]


TOOL_SELECTION_PROMPT = """
You are an expert in determining which tools are needed to solve a task.
You will receive a task description and a list of tool names.
You should return a a list of tools that you think are relevant to the task.
"""


class ToolSelection(BaseModel):
    """Tool selection."""

    tool_names: list[str]


def get_tool_schemas(integrations: list[str]) -> list[dict[str, Any]]:
    """Get tool schemas.

    Args:
        integrations (list[str]): A list of integration names.

    Returns:
        list[dict[str, Any]]: A list of tool schemas.

    """
    selected_integrations = [Integration(integration_str) for integration_str in integrations]

    tools_by_integration = get_integrations(selected_integrations)
    tool_schemas: list[dict[str, Any]] = []
    for integration in tools_by_integration:
        for tool_schema in tools_by_integration[integration]:
            if isinstance(tool_schema, dict) and "function" in tool_schema:
                tool_schemas.append(tool_schema)
    return tool_schemas


async def get_recommended_tools_async(description: str, tool_schemas: list[dict[str, Any]], **kwargs: Any) -> list[str]:
    """Get names of recommended tools for the given tool_schemas."""
    message = f"""
    Task Description: {description}
    Tool Names: {[t["function"]["name"] for t in tool_schemas]}
    Return a list of tools that are relevant to the task.
    """
    response = await acompletion(
        model=SELECTION_MODEL,
        messages=[{"role": "system", "content": TOOL_SELECTION_PROMPT}, {"role": "user", "content": message}],
        response_format=ToolSelection,
        **kwargs,
    )
    tool_selections = ToolSelection.model_validate_json(response.choices[0].message.content.strip())  # type: ignore[union-attr]

    return tool_selections.tool_names


def get_recommended_tools(description: str, tool_schemas: list[dict[str, Any]], **kwargs: Any) -> list[str]:
    """Get recommended tools for the given integrations."""
    return run_async_in_sync(get_recommended_tools_async(description, tool_schemas, **kwargs))
