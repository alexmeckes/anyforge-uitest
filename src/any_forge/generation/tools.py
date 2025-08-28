from typing import Any

from any_agent.utils import run_async_in_sync
from any_llm import acompletion
from pydantic import BaseModel

from any_forge.integrations import Integration, get_integrations

SELECTION_MODEL = "openai:gpt-5-nano"


class IntegrationSelection(BaseModel):
    """Integration selection."""

    integrations: list[str]


TOOL_SELECTION_PROMPT = """
You are an expert in determining which tools are needed to solve a task.
You will receive a task description and a list of tool names
You should return a a list of tools that you think are relevant to the task.
"""


class ToolSelection(BaseModel):
    """Tool selection."""

    tool_names: list[str]


async def get_recommended_tools_async(description: str, integrations: list[str], **kwargs: Any) -> list[dict[str, Any]]:
    """Get recommended tools for the given integrations."""
    selected_integrations = [Integration(integration_str) for integration_str in integrations]

    tools_by_integration = get_integrations(selected_integrations)
    tool_names: list[str] = []
    tool_schemas_by_name: dict[str, dict[str, Any]] = {}
    for integration in tools_by_integration:
        for tool_schema in tools_by_integration[integration]:
            if isinstance(tool_schema, dict) and "function" in tool_schema:
                tool_name = f"{integration}:{tool_schema['function']['name']}"
                tool_names.append(tool_name)
                tool_schemas_by_name[tool_name] = tool_schema

    message = f"""
    Task Description: {description}
    Tool Names: {tool_names}
    Return a list of tools that are relevant to the task.
    """
    response = await acompletion(
        model=SELECTION_MODEL,
        messages=[{"role": "system", "content": TOOL_SELECTION_PROMPT}, {"role": "user", "content": message}],
        response_format=ToolSelection,
        **kwargs,
    )
    tool_selections = ToolSelection.model_validate_json(response.choices[0].message.content.strip())  # type: ignore[union-attr]

    tool_schemas = []
    for tool_name in tool_selections.tool_names:
        if tool_name in tool_schemas_by_name:
            tool_schemas.append(tool_schemas_by_name[tool_name])

    return tool_schemas


def get_recommended_tools(description: str, integrations: list[str], **kwargs: Any) -> list[dict[str, Any]]:
    """Get recommended tools for the given integrations."""
    return run_async_in_sync(get_recommended_tools_async(description, integrations, **kwargs))
