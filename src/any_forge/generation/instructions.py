from collections.abc import Iterable
from typing import Any

from any_agent.frameworks.tinyagent import DEFAULT_SYSTEM_PROMPT
from any_llm import completion

INSTRUCTIONS_MODEL = "openai:gpt-5-nano"

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

OUTPUT_TEMPLATE = """
{base_instructions}
# General Instructions
{general_instructions}
# Reminders
- If a tool call fails with an error, don't try the same call again. Instead, try to understand the error and fix the root cause.

"""


class _InstructionGenerator:
    def __init__(self, task_description: str, tool_schemas: list[dict[str, Any]], **kwargs: Any):
        self.task_description = task_description
        self.tools = [f"{schema['function']['name']}: {schema['function']['description']}" for schema in tool_schemas]
        self.kwargs = kwargs
        self.general_instructions = ""
        self.base_instructions = DEFAULT_SYSTEM_PROMPT

    def generate(self) -> Iterable[str]:
        for chunk in completion(
            model=INSTRUCTIONS_MODEL,
            messages=[
                {"role": "system", "content": INSTRUCTIONS_PROMPT},
                {
                    "role": "user",
                    "content": f"Here is the task description: {self.task_description}\nAnd the list of tools that will be available: {self.tools}",
                },
            ],
            stream=True,
            **self.kwargs,
        ):
            content = chunk.choices[0].delta.content  # type: ignore[union-attr]
            if content:
                self.general_instructions += content
                yield content

    def get_full_instructions(self) -> str:
        return OUTPUT_TEMPLATE.format(
            general_instructions=self.general_instructions, base_instructions=self.base_instructions
        )
