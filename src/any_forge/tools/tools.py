from typing import Any

from any_llm import completion
from pydantic import BaseModel

from any_forge.tools.integrations import Integration, get_integrations

SELECTION_MODEL = "openai:gpt-5-nano"
INTEGRATION_SELECTION_PROMPT = """
You are an expert in determining which integrations are needed to solve a task.
You will receive a task description and a list of integrations.
You should return a list of integrations that are needed to solve the task.
"""


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


def get_recommended_tools(
    description: str, integrations: list[str], **kwargs: Any
) -> tuple[list[str], list[dict[str, Any]]]:
    """Get recommended tools for the given integrations."""
    message = f"""
    Task Description: {description}
    Integrations: {integrations}
    Return a list of integrations that are relevant to the task.
    """
    # Step 1: Narrow down which integrations are needed
    response = completion(
        model=SELECTION_MODEL,
        messages=[{"role": "system", "content": INTEGRATION_SELECTION_PROMPT}, {"role": "user", "content": message}],
        response_format=IntegrationSelection,
        **kwargs,
    )
    integration_selections = IntegrationSelection.model_validate_json(response.choices[0].message.content.strip())  # type: ignore[union-attr]

    # Convert string integration names back to Integration enums
    selected_integrations = []
    for integration_str in integration_selections.integrations:
        try:
            selected_integrations.append(Integration(integration_str))
        except ValueError:
            # Skip invalid integration names
            continue

    tools_by_integration = get_integrations(selected_integrations)
    tool_names: list[str] = []
    tool_schemas_by_name: dict[str, dict[str, Any]] = {}
    for integration in tools_by_integration:
        for tool_schema in tools_by_integration[integration]:
            if isinstance(tool_schema, dict) and "function" in tool_schema:
                tool_name = f"{integration}:{tool_schema['function']['name']}"
                tool_names.append(tool_name)
                tool_schemas_by_name[tool_name] = tool_schema

    # Step 2, narrow down which tools from the relevant integrations are needed
    message = f"""
    Task Description: {description}
    Tool Names: {tool_names}
    Return a list of tools that are relevant to the task.
    """
    response = completion(
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

    return integration_selections.integrations, tool_schemas
