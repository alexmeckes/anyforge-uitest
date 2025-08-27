from typing import Any

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
# General Instructions
{general_instructions}
# Reminders
- If a tool call fails with an error, don't try the same call again. Instead, try to understand the error and fix the root cause.
"""


def generate_instructions(task_description: str, **kwargs: Any) -> str:
    """Generate instructions based on the task description."""
    response = completion(
        model=INSTRUCTIONS_MODEL,
        messages=[{"role": "system", "content": INSTRUCTIONS_PROMPT}, {"role": "user", "content": task_description}],
        **kwargs,
    )
    general_instructions = response.choices[0].message.content.strip()  # type: ignore[union-attr]
    return OUTPUT_TEMPLATE.format(general_instructions=general_instructions)
