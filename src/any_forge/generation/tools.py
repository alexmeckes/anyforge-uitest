from typing import Any

from any_llm import acompletion
from any_llm.utils.aio import run_async_in_sync
from pydantic import BaseModel

SELECTION_MODEL = "openai:gpt-4.1-mini"

TOOL_SELECTION_PROMPT = """
You are an expert in determining which tools are needed to solve a task.
You will receive a task description and a list of tool names.
You should return a a list of tools that you think are relevant to the task.
"""


class ToolSelection(BaseModel):
    """Tool selection."""

    tool_names: list[str]


async def get_recommended_tools_async(description: str, tool_names: list[str], **kwargs: Any) -> list[str]:
    """Get names of recommended tools for the given tool_names."""
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
    return tool_selections.tool_names


def get_recommended_tools(description: str, tool_names: list[str], **kwargs: Any) -> list[str]:
    """Get recommended tools for the given integrations."""
    return run_async_in_sync(get_recommended_tools_async(description, tool_names, **kwargs))
