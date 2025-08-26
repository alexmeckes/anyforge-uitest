from enum import StrEnum


class AgentCreationState(StrEnum):
    """Enum for the different states of the agent creation process."""

    INIT = "init"
    SELECT_MODEL = "select_model"
    SELECT_INTEGRATIONS = "select_integrations"
    CREATE_PROMPT = "select_prompt"
    REVIEW = "select_review"
    COMPLETE = "complete"


class AgentStateMachine:
    """State machine for the agent builder."""

    def __init__(self) -> None:
        """Initialize the state machine."""
        self.state: AgentCreationState = AgentCreationState.INIT

    def next_state(self) -> None:
        """Advance to the next state in the creation process."""
        if self.state == AgentCreationState.INIT:
            self.state = AgentCreationState.SELECT_MODEL
        elif self.state == AgentCreationState.SELECT_MODEL:
            self.state = AgentCreationState.SELECT_INTEGRATIONS
        elif self.state == AgentCreationState.SELECT_INTEGRATIONS:
            self.state = AgentCreationState.CREATE_PROMPT
        elif self.state == AgentCreationState.CREATE_PROMPT:
            self.state = AgentCreationState.REVIEW
        elif self.state == AgentCreationState.REVIEW:
            self.state = AgentCreationState.COMPLETE

    def previous_state(self) -> None:
        """Go back to the previous state."""
        if self.state == AgentCreationState.INIT:
            self.state = AgentCreationState.INIT
        elif self.state == AgentCreationState.SELECT_MODEL:
            self.state = AgentCreationState.INIT
        elif self.state == AgentCreationState.SELECT_INTEGRATIONS:
            self.state = AgentCreationState.SELECT_MODEL
        elif self.state == AgentCreationState.CREATE_PROMPT:
            self.state = AgentCreationState.SELECT_INTEGRATIONS
        elif self.state == AgentCreationState.REVIEW:
            self.state = AgentCreationState.CREATE_PROMPT
        elif self.state == AgentCreationState.COMPLETE:
            self.state = AgentCreationState.REVIEW

    def can_advance(self) -> bool:
        """Return True for now."""
        return True

    def reset(self) -> None:
        """Reset the state machine to initial state."""
        self.state = AgentCreationState.INIT
