import uuid
from typing import Any

from any_agent import AgentConfig, AgentTrace
from any_agent.callbacks import Callback
from pydantic import BaseModel, ConfigDict, Field, field_serializer

from any_forge.integrations import create_tool_callable


class AgentForgeAgent(BaseModel):
    """Agent for the forge."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    integrations: list[str] = Field(default_factory=list)

    task_description: str | None = None

    instructions: str | None = None

    run_kwargs: dict[str, Any] = Field(default_factory=dict)

    callbacks: list[Callback] = Field(default_factory=list)

    model_id: str | None = None
    prompt: str | None = None
    tools: list[dict[str, Any]] = Field(default_factory=list)

    traces: list[AgentTrace] = Field(default_factory=list)

    @field_serializer("callbacks", when_used="json")
    def serialize_callbacks(self, callbacks: list[Callback]) -> None:
        """Serialize the callbacks."""
        # Return None or empty list to exclude from serialization
        # https://github.com/mozilla-ai/any-forge/issues/14
        return

    def _check_fully_defined(self) -> bool:
        for attr in ("model_id", "instructions", "tools"):
            if getattr(self, attr) is None:
                err_msg = f"{attr} is required"
                raise ValueError(err_msg)
        if not self.tools:
            err_msg = "tools is required"
            raise ValueError(err_msg)
        return True

    def get_agent_config(self) -> AgentConfig:
        """Get the agent config."""
        self._check_fully_defined()

        wrapped_tools: list[Any] = []
        for tool in self.tools:
            wrapped_tools.append(create_tool_callable(tool["function"]))

        return AgentConfig(
            model_id=str(self.model_id), tools=wrapped_tools, callbacks=self.callbacks, instructions=self.instructions
        )

    def get_prompt(self) -> str:
        """Get the prompt to use when running the agent."""
        self._check_fully_defined()
        if self.prompt is None:
            self.prompt = ""
        return self.prompt

    def get_kwargs(self) -> dict[str, Any]:
        """Get the kwargs used when running the agent."""
        return self.run_kwargs
