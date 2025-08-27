from unittest.mock import MagicMock, patch

from any_forge.generation.instructions import INSTRUCTIONS_MODEL, INSTRUCTIONS_PROMPT, _InstructionGenerator


def test_generate_instructions() -> None:
    with patch("any_forge.generation.instructions.completion") as mock_completion:
        # completion returns a generator, we will mock a single return of that
        mock_chunk = MagicMock()
        mock_chunk.choices[0].delta.content = "Here are the instructions."
        mock_completion.return_value = [mock_chunk]

        generator = _InstructionGenerator("Task description")
        for _ in generator.generate():
            pass
        result = generator.get_full_instructions()

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
