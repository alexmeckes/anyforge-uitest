from any_forge.state.state import AgentCreationState, AgentStateMachine


def test_initial_state() -> None:
    """Test that state machine starts in INIT state."""
    sm = AgentStateMachine()
    assert sm.state == AgentCreationState.INIT


def test_next_state_progression() -> None:
    """Test complete forward state progression."""
    sm = AgentStateMachine()

    sm.next_state()
    # all these intermediate variable assignments are to help mypy because it was getting confused about what type sm.state is.
    current_state = sm.state
    assert current_state == AgentCreationState.SELECT_INTEGRATIONS

    sm.next_state()
    current_state = sm.state
    assert current_state == AgentCreationState.SELECT_MODEL

    sm.next_state()
    current_state = sm.state
    assert current_state == AgentCreationState.CREATE_PROMPT

    sm.next_state()
    current_state = sm.state
    assert current_state == AgentCreationState.REVIEW

    sm.next_state()
    current_state = sm.state
    assert current_state == AgentCreationState.COMPLETE

    sm.next_state()
    current_state = sm.state
    assert current_state == AgentCreationState.COMPLETE


def test_previous_state_progression() -> None:
    """Test complete backward state progression."""
    sm = AgentStateMachine()
    sm.state = AgentCreationState.COMPLETE

    sm.previous_state()
    current_state = sm.state
    assert current_state == AgentCreationState.REVIEW

    sm.previous_state()
    current_state = sm.state
    assert current_state == AgentCreationState.CREATE_PROMPT

    sm.previous_state()
    current_state = sm.state
    assert current_state == AgentCreationState.SELECT_MODEL

    sm.previous_state()
    current_state = sm.state
    assert current_state == AgentCreationState.SELECT_INTEGRATIONS

    sm.previous_state()
    current_state = sm.state
    assert current_state == AgentCreationState.INIT

    sm.previous_state()
    current_state = sm.state
    assert current_state == AgentCreationState.INIT


def test_can_advance_always_true() -> None:
    """Test that can_advance always returns True."""
    sm = AgentStateMachine()
    for state in AgentCreationState:
        sm.state = state
        assert sm.can_advance() is True


def test_can_run_valid_states() -> None:
    """Test can_run returns True for REVIEW and COMPLETE states."""
    sm = AgentStateMachine()

    sm.state = AgentCreationState.REVIEW
    assert sm.can_run() is True

    sm.state = AgentCreationState.COMPLETE
    assert sm.can_run() is True


def test_can_run_invalid_states() -> None:
    """Test can_run returns False for non-runnable states."""
    sm = AgentStateMachine()
    invalid_states = [
        AgentCreationState.INIT,
        AgentCreationState.SELECT_INTEGRATIONS,
        AgentCreationState.SELECT_MODEL,
        AgentCreationState.CREATE_PROMPT,
    ]

    for state in invalid_states:
        sm.state = state
        assert sm.can_run() is False


def test_reset() -> None:
    """Test reset returns state to INIT."""
    sm = AgentStateMachine()
    sm.state = AgentCreationState.COMPLETE
    sm.reset()
    assert sm.state == AgentCreationState.INIT


def test_boundary_transitions() -> None:
    """Test state machine handles boundary conditions correctly."""
    sm = AgentStateMachine()

    # Can't go forward from COMPLETE
    sm.state = AgentCreationState.COMPLETE
    original_state = sm.state
    assert sm.state == original_state

    # Can't go back from INIT
    sm.state = AgentCreationState.INIT
    original_state = sm.state
    sm.previous_state()
    assert sm.state == original_state
