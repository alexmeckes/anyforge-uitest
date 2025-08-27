from collections.abc import Iterable
from typing import Any

from any_agent.frameworks.tinyagent import DEFAULT_SYSTEM_PROMPT
from any_llm import completion

INSTRUCTIONS_MODEL = "openai:gpt-5-nano"
INSTRUCTIONS_PROMPT = """
You are an expert in providing detailed instructions.
You will receive a task description and your job is to provide instructions for an LLM Agent that will try to solve the task.
The instructions should be concise, clear, and actionable.
Don't include detailed steps to be followed, the LLM Agent should be able to figure out
the best course of action from your instructions and the provided tools.
"""

OUTPUT_TEMPLATE = """
{base_instructions}
# General Instructions
{general_instructions}
# Reminders
- If a tool call fails with an error, don't try the same call again. Instead, try to understand the error and fix the root cause.

"""


class _InstructionGenerator:
    def __init__(self, task_description: str, **kwargs: Any):
        self.task_description = task_description
        self.kwargs = kwargs
        self.general_instructions = ""
        self.base_instructions = DEFAULT_SYSTEM_PROMPT

    def generate(self) -> Iterable[str]:
        for chunk in completion(
            model=INSTRUCTIONS_MODEL,
            messages=[
                {"role": "system", "content": INSTRUCTIONS_PROMPT},
                {"role": "user", "content": self.task_description},
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
