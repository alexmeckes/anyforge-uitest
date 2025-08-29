from unittest.mock import MagicMock, patch

from any_forge.generation.instructions import (
    INSTRUCTIONS_MODEL,
    INSTRUCTIONS_PROMPT,
    generate_instructions,
    tool_schemas_to_strings,
)


def test_generate_instructions() -> None:
    with patch("any_forge.generation.instructions.completion") as mock_completion:
        # completion returns a generator, we will mock a single return of that
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Here are the instructions."
        mock_completion.return_value = mock_response

        task_description = "Task description"
        tools = [{"function": {"name": "tool1", "description": "Tool 1 description"}}]
        converted_tools = tool_schemas_to_strings(tools)
        result = generate_instructions(task_description, tools)

        assert mock_completion.call_args[1]["model"] == INSTRUCTIONS_MODEL
        messages = mock_completion.call_args[1]["messages"]
        assert messages == [
            {"role": "system", "content": INSTRUCTIONS_PROMPT},
            {
                "role": "user",
                "content": f"Here is the task description: {task_description}\nThe list of tools that will be available: {converted_tools}",
            },
        ]
        assert "Here are the instructions." in result
