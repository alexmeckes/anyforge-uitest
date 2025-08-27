import uuid
from enum import StrEnum

from pydantic import BaseModel, Field


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

    def reset(self) -> None:
        """Reset the state machine to initial state."""
        self.state = AgentCreationState.INIT


class AgentForgeAgent(BaseModel):
    """Agent for the forge."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    state_machine: AgentStateMachine = Field(default_factory=AgentStateMachine)
