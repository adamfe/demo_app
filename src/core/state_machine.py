"""
State Machine for Voice Mode

Manages application state transitions and ensures valid state flow.
"""

from enum import Enum
from typing import Optional, Callable, Dict
from datetime import datetime


class AppState(Enum):
    """Application states"""
    INITIALIZING = "initializing"      # App starting up
    IDLE = "idle"                      # Ready to record
    RECORDING = "recording"            # Recording audio
    PROCESSING = "processing"          # Transcribing with Whisper
    REFINING = "refining"              # Refining with Claude
    COPYING = "copying"                # Copying to clipboard
    ERROR = "error"                    # Error occurred
    PAUSED = "paused"                  # App paused by user


class StateMachine:
    """
    Manages application state with transitions and callbacks

    Valid transitions:
    INITIALIZING -> IDLE
    IDLE -> RECORDING
    RECORDING -> PROCESSING (if audio captured)
    RECORDING -> IDLE (if no audio captured)
    PROCESSING -> REFINING (if Claude enabled)
    PROCESSING -> COPYING (if Claude disabled)
    REFINING -> COPYING
    COPYING -> IDLE
    ANY -> ERROR
    ANY -> PAUSED
    PAUSED -> IDLE
    ERROR -> IDLE
    """

    def __init__(self):
        self.current_state = AppState.INITIALIZING
        self.previous_state: Optional[AppState] = None
        self.state_history: list[tuple[AppState, datetime]] = []

        # State callbacks: Dict[state, callback]
        self.on_state_enter: Dict[AppState, Callable] = {}
        self.on_state_exit: Dict[AppState, Callable] = {}

        # Metadata for current state
        self.state_data: dict = {}

    def transition_to(self, new_state: AppState, **kwargs) -> bool:
        """
        Transition to a new state

        Args:
            new_state: Target state
            **kwargs: Additional data to store with state

        Returns:
            True if transition was successful
        """
        # Validate transition
        if not self._is_valid_transition(self.current_state, new_state):
            print(f"✗ Invalid state transition: {self.current_state.value} -> {new_state.value}")
            return False

        # Call exit callback for current state
        if self.current_state in self.on_state_exit:
            try:
                self.on_state_exit[self.current_state]()
            except Exception as e:
                print(f"Error in state exit callback: {e}")

        # Update state
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_data = kwargs

        # Record in history
        self.state_history.append((new_state, datetime.now()))

        # Call enter callback for new state
        if new_state in self.on_state_enter:
            try:
                self.on_state_enter[new_state](**kwargs)
            except Exception as e:
                print(f"Error in state enter callback: {e}")

        print(f"State: {self.previous_state.value} → {new_state.value}")
        return True

    def _is_valid_transition(self, from_state: AppState, to_state: AppState) -> bool:
        """
        Check if a state transition is valid

        Args:
            from_state: Current state
            to_state: Target state

        Returns:
            True if transition is allowed
        """
        # ERROR and PAUSED can be entered from any state
        if to_state in (AppState.ERROR, AppState.PAUSED):
            return True

        # Can return to IDLE from ERROR or PAUSED
        if to_state == AppState.IDLE and from_state in (AppState.ERROR, AppState.PAUSED):
            return True

        # Define valid transitions
        valid_transitions = {
            AppState.INITIALIZING: [AppState.IDLE],
            AppState.IDLE: [AppState.RECORDING],
            AppState.RECORDING: [AppState.PROCESSING, AppState.IDLE],  # Can return to IDLE if no audio
            AppState.PROCESSING: [AppState.REFINING, AppState.COPYING],
            AppState.REFINING: [AppState.COPYING],
            AppState.COPYING: [AppState.IDLE],
        }

        return to_state in valid_transitions.get(from_state, [])

    def register_callback(self, state: AppState, on_enter: Optional[Callable] = None, on_exit: Optional[Callable] = None) -> None:
        """
        Register callbacks for state transitions

        Args:
            state: State to register callback for
            on_enter: Callback when entering state (receives **kwargs from transition_to)
            on_exit: Callback when exiting state
        """
        if on_enter:
            self.on_state_enter[state] = on_enter
        if on_exit:
            self.on_state_exit[state] = on_exit

    def get_state(self) -> AppState:
        """Get current state"""
        return self.current_state

    def get_state_data(self, key: str, default=None):
        """Get data associated with current state"""
        return self.state_data.get(key, default)

    def is_state(self, *states: AppState) -> bool:
        """
        Check if current state matches any of the given states

        Args:
            *states: States to check against

        Returns:
            True if current state is in the list
        """
        return self.current_state in states

    def is_busy(self) -> bool:
        """Check if app is busy (recording, processing, refining, copying)"""
        return self.current_state in (
            AppState.RECORDING,
            AppState.PROCESSING,
            AppState.REFINING,
            AppState.COPYING
        )

    def is_ready(self) -> bool:
        """Check if app is ready to record"""
        return self.current_state == AppState.IDLE

    def get_state_description(self) -> str:
        """
        Get human-readable description of current state

        Returns:
            Description string
        """
        descriptions = {
            AppState.INITIALIZING: "Starting up...",
            AppState.IDLE: "Ready to dictate",
            AppState.RECORDING: "Recording...",
            AppState.PROCESSING: "Transcribing...",
            AppState.REFINING: "Refining with Claude...",
            AppState.COPYING: "Copying to clipboard...",
            AppState.ERROR: "Error occurred",
            AppState.PAUSED: "Paused",
        }
        return descriptions.get(self.current_state, "Unknown state")

    def reset(self) -> None:
        """Reset state machine to IDLE"""
        self.current_state = AppState.IDLE
        self.previous_state = None
        self.state_data = {}

    def get_state_duration(self) -> float:
        """
        Get duration of current state in seconds

        Returns:
            Duration in seconds
        """
        if not self.state_history:
            return 0.0

        last_transition = self.state_history[-1][1]
        return (datetime.now() - last_transition).total_seconds()


def test_state_machine():
    """Test the state machine"""
    sm = StateMachine()

    # Register callbacks
    def on_enter_recording(**kwargs):
        print(f"  → Entered RECORDING state with data: {kwargs}")

    def on_exit_recording():
        print("  ← Exiting RECORDING state")

    sm.register_callback(AppState.RECORDING, on_enter=on_enter_recording, on_exit=on_exit_recording)

    # Test valid transitions
    print("Testing valid transitions:")
    assert sm.transition_to(AppState.IDLE), "Should transition to IDLE"
    assert sm.transition_to(AppState.RECORDING, duration=3.5), "Should transition to RECORDING"
    assert sm.transition_to(AppState.PROCESSING), "Should transition to PROCESSING"
    assert sm.transition_to(AppState.REFINING), "Should transition to REFINING"
    assert sm.transition_to(AppState.COPYING), "Should transition to COPYING"
    assert sm.transition_to(AppState.IDLE), "Should transition back to IDLE"

    # Test invalid transition
    print("\nTesting invalid transition:")
    assert not sm.transition_to(AppState.RECORDING), "Should stay in IDLE (invalid)"

    # Test emergency transitions
    print("\nTesting emergency transitions:")
    assert sm.transition_to(AppState.ERROR), "Should transition to ERROR from any state"
    assert sm.transition_to(AppState.IDLE), "Should recover from ERROR to IDLE"

    # Test state checks
    print("\nTesting state checks:")
    sm.transition_to(AppState.RECORDING)
    assert sm.is_state(AppState.RECORDING), "Should be in RECORDING"
    assert sm.is_busy(), "Should be busy"
    assert not sm.is_ready(), "Should not be ready"

    sm.transition_to(AppState.PROCESSING)
    sm.transition_to(AppState.COPYING)
    sm.transition_to(AppState.IDLE)
    assert sm.is_ready(), "Should be ready"
    assert not sm.is_busy(), "Should not be busy"

    print("\n✓ All state machine tests passed!")


if __name__ == "__main__":
    test_state_machine()
