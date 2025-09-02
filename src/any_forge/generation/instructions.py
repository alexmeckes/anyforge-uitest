from typing import Any

from any_llm import completion

INSTRUCTIONS_MODEL = "openai:gpt-4.1-mini"

INSTRUCTIONS_PROMPT = """
You are an expert in providing instructions for LLM Agents.
You will receive a task description and a list of available tools and your job is to return instructions for an LLM Agent that will try to solve the task.
The instructions should follow the following output format:

# Goal

A 1-paragraph, high-level description of the task the agent will need to solve.

# Steps

A small bullet-point list describing to the agent what is the high-level sequence of steps to follow.
Don't make the list too detailed, leave room for the agent to fill in the gaps.
"""


def tool_schemas_to_strings(tool_schemas: list[dict[str, Any]]) -> list[str]:
    """Convert tool schemas to a list of strings."""
    return [f"{schema['function']['name']}: {schema['function']['description']}" for schema in tool_schemas]


def generate_instructions(task_description: str, tool_schemas: list[dict[str, Any]], **kwargs: Any) -> str:
    """Generate instructions for an LLM Agent based on the task description and available tools."""
    tools = tool_schemas_to_strings(tool_schemas)
    response = completion(
        model=INSTRUCTIONS_MODEL,
        messages=[
            {"role": "system", "content": INSTRUCTIONS_PROMPT},
            {
                "role": "user",
                "content": f"Here is the task description: {task_description}\nThe list of tools that will be available: {tools}",
            },
        ],
        **kwargs,
    )
    return str(response.choices[0].message.content)  # type: ignore[union-attr]
