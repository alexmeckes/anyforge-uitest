from typing import TYPE_CHECKING, Any

from any_llm import completion
from pydantic import BaseModel

if TYPE_CHECKING:
    from any_llm.types.completion import ChatCompletion

EVALUATION_MODEL = "openai:gpt-4.1-mini"

EVALUATION_PROMPT = """
You are an expert in providing evaluation criteria to analyze AI Agents.
You will receive the following:

* A task description
* A list of tools that the agent will use
* A list of existing evaluation criteria

Your job is to return what you believe is the SINGLE most valuable evaluation criteria that will help determine whether the agent was successful.
Make sure your evaluation criteria is evaluating the agent in some different way from all the other existing evaluation criteria.
"""


class EvaluationOutput(BaseModel):
    """Evaluation output."""

    answer: str


def generate_evaluation(task_description: str, tools: list[str], existing_evaluations: list[str], **kwargs: Any) -> str:
    """Generate instructions for an LLM Agent based on the task description and available tools."""
    response: ChatCompletion = completion(  # type: ignore[assignment]
        model=EVALUATION_MODEL,
        messages=[
            {"role": "system", "content": EVALUATION_PROMPT},
            {
                "role": "user",
                "content": f"Here is the task description: {task_description}\nThe list of tools that will be available: {tools}\nThe list of existing evaluation criteria: {existing_evaluations}",
            },
        ],
        response_format=EvaluationOutput,
        **kwargs,
    )

    content = response.choices[0].message.content
    if not content:
        err_msg = "No content returned from the evaluation model."
        raise ValueError(err_msg)
    result = EvaluationOutput.model_validate_json(content)
    return result.answer
