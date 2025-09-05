from unittest.mock import MagicMock, patch

from any_forge.generation.instructions import (
    INSTRUCTIONS_MODEL,
    INSTRUCTIONS_PROMPT,
    generate_instructions,
)


def test_generate_instructions() -> None:
    with patch("any_forge.generation.instructions.completion") as mock_completion:
        # completion returns a generator, we will mock a single return of that
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Here are the instructions."
        mock_completion.return_value = mock_response

        task_description = "Task description"
        tools = ["tool1", "tool_2"]
        result = generate_instructions(task_description, tools)

        assert mock_completion.call_args[1]["model"] == INSTRUCTIONS_MODEL
        messages = mock_completion.call_args[1]["messages"]
        assert messages == [
            {"role": "system", "content": INSTRUCTIONS_PROMPT},
            {
                "role": "user",
                "content": f"Here is the task description: {task_description}\nThe list of tools that will be available: {tools}",
            },
        ]
        assert "Here are the instructions." in result
