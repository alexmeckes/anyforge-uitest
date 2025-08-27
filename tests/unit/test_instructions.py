from unittest.mock import patch

from any_forge.generation.instructions import INSTRUCTIONS_MODEL, INSTRUCTIONS_PROMPT, generate_instructions


def test_generate_instructions() -> None:
    with patch("any_forge.generation.instructions.completion") as mock_completion:
        mock_completion.return_value.choices[0].message.content = "Here are the instructions."

        result = generate_instructions("Task description")

        assert mock_completion.call_args[1]["model"] == INSTRUCTIONS_MODEL
        messages = mock_completion.call_args[1]["messages"]
        assert messages == [
            {"role": "system", "content": INSTRUCTIONS_PROMPT},
            {"role": "user", "content": "Task description"},
        ]
        assert "# General Instructions" in result
        assert "Here are the instructions." in result
        assert "# Reminders" in result
        assert (
            "- If a tool call fails with an error, don't try the same call again. Instead, try to understand the error and fix the root cause."
            in result
        )
