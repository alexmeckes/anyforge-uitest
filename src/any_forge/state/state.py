import uuid
from enum import StrEnum
from typing import Any

from any_agent import AgentConfig
from any_agent.callbacks import Callback
from any_agent.config import Tool
from pydantic import BaseModel, ConfigDict, Field, field_serializer


class AgentCreationState(StrEnum):
    """Enum for the different states of the agent creation process."""

    INIT = "init"
    SELECT_INTEGRATIONS = "select_integrations"
    SELECT_MODEL = "select_model"
    CREATE_PROMPT = "create_prompt"
    REVIEW = "review"
    COMPLETE = "complete"


class AgentStateMachine(BaseModel):
    """State machine for the agent builder."""

    state: AgentCreationState = AgentCreationState.INIT

    def next_state(self) -> None:
        """Advance to the next state in the creation process."""
        if self.state == AgentCreationState.INIT:
            self.state = AgentCreationState.SELECT_INTEGRATIONS
        elif self.state == AgentCreationState.SELECT_INTEGRATIONS:
            self.state = AgentCreationState.SELECT_MODEL
        elif self.state == AgentCreationState.SELECT_MODEL:
            self.state = AgentCreationState.CREATE_PROMPT
        elif self.state == AgentCreationState.CREATE_PROMPT:
            self.state = AgentCreationState.REVIEW
        elif self.state == AgentCreationState.REVIEW:
            self.state = AgentCreationState.COMPLETE
        elif self.state == AgentCreationState.COMPLETE:
            pass  # do nothing

    def previous_state(self) -> None:
        """Go back to the previous state."""
        if self.state == AgentCreationState.SELECT_INTEGRATIONS:
            self.state = AgentCreationState.INIT
        elif self.state == AgentCreationState.SELECT_MODEL:
            self.state = AgentCreationState.SELECT_INTEGRATIONS
        elif self.state == AgentCreationState.CREATE_PROMPT:
            self.state = AgentCreationState.SELECT_MODEL
        elif self.state == AgentCreationState.REVIEW:
            self.state = AgentCreationState.CREATE_PROMPT
        elif self.state == AgentCreationState.COMPLETE:
            self.state = AgentCreationState.REVIEW
        elif self.state == AgentCreationState.INIT:
            pass  # do nothing

    def can_advance(self) -> bool:
        """Return True for now."""
        return True

    def can_run(self) -> bool:
        """Return True if the agent can be run."""
        if self.state not in [AgentCreationState.REVIEW, AgentCreationState.COMPLETE]:
            return False
        return True

    def reset(self) -> None:
        """Reset the state machine to initial state."""
        self.state = AgentCreationState.INIT


class AgentForgeAgent(BaseModel):
    """Agent for the forge."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    state_machine: AgentStateMachine = Field(default_factory=AgentStateMachine)
    instructions: str | None = None

    run_kwargs: dict[str, Any] = Field(default_factory=dict)

    callbacks: list[Callback] = Field(default_factory=list)

    model_id: str | None = None
    tools: list[Tool] = Field(default_factory=list)

    @field_serializer("callbacks", when_used="json")
    def serialize_callbacks(self, callbacks: list[Callback]) -> None:
        """Serialize the callbacks."""
        # Return None or empty list to exclude from serialization
        # https://github.com/mozilla-ai/any-forge/issues/14
        return

    def get_agent_config(self) -> AgentConfig:
        """Get the agent config."""
        if not self.state_machine.can_run():
            msg = f"Agent cannot create config: state is {self.state_machine.state}"
            raise ValueError(msg)

        if self.model_id is None:
            err_msg = "model_id is required"
            raise ValueError(err_msg)

        return AgentConfig(
            model_id=self.model_id, tools=self.tools, callbacks=self.callbacks, instructions=self.instructions
        )  # after https://github.com/mozilla-ai/any-forge/issues/3 this can be a real value

    def get_prompt(self) -> str:
        """Get the prompt to use when running the agent."""
        if not self.state_machine.can_run():
            msg = f"Agent cannot get prompt: state is {self.state_machine.state}"
            raise ValueError(msg)
        return "I'm a prompt"  # after https://github.com/mozilla-ai/any-forge/issues/3 this can be a real value

    def get_kwargs(self) -> dict[str, Any]:
        """Get the kwargs used when running the agent."""
        return self.run_kwargs
