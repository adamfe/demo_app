"""
Hotkey Manager for Voice Mode

Handles keyboard hotkey detection including Caps Lock monitoring.
Caps Lock is tricky on macOS - we monitor its state changes.
"""

import threading
from typing import Callable, Optional
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
from enum import Enum


class HotkeyType(Enum):
    """Supported hotkey types"""
    CAPS_LOCK = "caps_lock"
    FN = "fn"
    OPTION_SPACE = "option+space"
    CONTROL_COMMAND_SPACE = "control+command+space"
    CUSTOM = "custom"


class HotkeyManager:
    """
    Manages hotkey detection for starting/stopping recording

    Caps Lock is handled specially - we monitor its state (on/off)
    rather than press/release events since it's a toggle key.
    """

    def __init__(self, hotkey_type: str = "caps_lock"):
        """
        Initialize hotkey manager

        Args:
            hotkey_type: Type of hotkey ("caps_lock", "option+space", etc.)
        """
        self.hotkey_type = hotkey_type
        self.is_recording = False
        self.caps_lock_state = False

        # Callbacks
        self.on_start_recording: Optional[Callable] = None
        self.on_stop_recording: Optional[Callable] = None

        # Keyboard listener
        self.listener: Optional[keyboard.Listener] = None
        self.running = False

        # For combination keys
        self.pressed_keys = set()

    def set_callbacks(self, on_start: Callable, on_stop: Callable) -> None:
        """
        Set callback functions

        Args:
            on_start: Called when recording should start
            on_stop: Called when recording should stop
        """
        self.on_start_recording = on_start
        self.on_stop_recording = on_stop

    def _handle_caps_lock(self) -> None:
        """Handle Caps Lock state change"""
        new_state = self._get_caps_lock_state()

        if new_state != self.caps_lock_state:
            self.caps_lock_state = new_state
            print(f"⌨️  Caps Lock state changed: {new_state}")

            if new_state:
                # Caps Lock turned ON - start recording
                if not self.is_recording:
                    self.is_recording = True
                    print("  → Starting recording (Caps Lock ON)")
                    if self.on_start_recording:
                        self.on_start_recording()
            else:
                # Caps Lock turned OFF - stop recording
                if self.is_recording:
                    self.is_recording = False
                    print("  → Stopping recording (Caps Lock OFF)")
                    if self.on_stop_recording:
                        self.on_stop_recording()

    def _get_caps_lock_state(self) -> bool:
        """
        Get current Caps Lock state

        Returns:
            True if Caps Lock is ON, False otherwise
        """
        try:
            # Try to use Quartz to get modifier state
            from Quartz import CGEventSourceFlagsState, kCGEventSourceStateCombinedSessionState
            from Quartz import kCGEventFlagMaskAlphaShift

            modifiers = CGEventSourceFlagsState(kCGEventSourceStateCombinedSessionState)
            return bool(modifiers & kCGEventFlagMaskAlphaShift)
        except Exception as e:
            print(f"Error getting Caps Lock state: {e}")
            return False

    def _on_press(self, key) -> None:
        """Handle key press events"""
        # Add to pressed keys
        self.pressed_keys.add(key)

        if self.hotkey_type == "caps_lock":
            # For Caps Lock, we check state on each key event
            # This ensures we catch Caps Lock even if press/release isn't detected
            self._handle_caps_lock()

        elif self.hotkey_type == "option+space":
            # Check if Option+Space is pressed
            if (Key.alt in self.pressed_keys or Key.alt_l in self.pressed_keys or Key.alt_r in self.pressed_keys) and Key.space in self.pressed_keys:
                if not self.is_recording:
                    self.is_recording = True
                    if self.on_start_recording:
                        self.on_start_recording()

        elif self.hotkey_type == "control+command+space":
            # Check if Control+Command+Space is pressed
            ctrl_pressed = Key.ctrl in self.pressed_keys or Key.ctrl_l in self.pressed_keys or Key.ctrl_r in self.pressed_keys
            cmd_pressed = Key.cmd in self.pressed_keys or Key.cmd_l in self.pressed_keys or Key.cmd_r in self.pressed_keys

            if ctrl_pressed and cmd_pressed and Key.space in self.pressed_keys:
                if not self.is_recording:
                    self.is_recording = True
                    if self.on_start_recording:
                        self.on_start_recording()

        elif self.hotkey_type == "fn":
            # Fn key detection (may not work on all keyboards)
            if key == Key.f13:  # Fn often maps to F13 or similar
                if not self.is_recording:
                    self.is_recording = True
                    if self.on_start_recording:
                        self.on_start_recording()

    def _on_release(self, key) -> None:
        """Handle key release events"""
        # Remove from pressed keys
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

        if self.hotkey_type == "caps_lock":
            # Check Caps Lock state again on release
            self._handle_caps_lock()

        elif self.hotkey_type == "option+space":
            # Stop recording when either key is released
            if key == Key.space or key == Key.alt or key == Key.alt_l or key == Key.alt_r:
                if self.is_recording:
                    self.is_recording = False
                    if self.on_stop_recording:
                        self.on_stop_recording()

        elif self.hotkey_type == "control+command+space":
            # Stop recording when Space is released
            if key == Key.space:
                if self.is_recording:
                    self.is_recording = False
                    if self.on_stop_recording:
                        self.on_stop_recording()

        elif self.hotkey_type == "fn":
            if key == Key.f13:
                if self.is_recording:
                    self.is_recording = False
                    if self.on_stop_recording:
                        self.on_stop_recording()

    def start(self) -> None:
        """Start listening for hotkey events"""
        if self.running:
            return

        self.running = True

        # Start keyboard listener
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()

        print(f"✓ Hotkey manager started (type: {self.hotkey_type})")

    def stop(self) -> None:
        """Stop listening for hotkey events"""
        if not self.running:
            return

        self.running = False

        if self.listener:
            self.listener.stop()
            self.listener = None

        print("✓ Hotkey manager stopped")

    def is_running(self) -> bool:
        """Check if hotkey manager is running"""
        return self.running

    def get_hotkey_description(self) -> str:
        """
        Get human-readable description of current hotkey

        Returns:
            Description string
        """
        descriptions = {
            "caps_lock": "Hold Caps Lock",
            "option+space": "Hold Option+Space",
            "control+command+space": "Hold Control+Command+Space",
            "fn": "Hold Fn key"
        }
        return descriptions.get(self.hotkey_type, "Custom hotkey")


def test_hotkey_manager():
    """Test the hotkey manager"""
    import time

    def on_start():
        print("🔴 RECORDING STARTED")

    def on_stop():
        print("⚫ RECORDING STOPPED")

    # Test with Caps Lock
    print("Testing Caps Lock hotkey...")
    print("Press Caps Lock to toggle recording")
    print("Press Ctrl+C to exit\n")

    manager = HotkeyManager(hotkey_type="caps_lock")
    manager.set_callbacks(on_start, on_stop)
    manager.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
        manager.stop()


if __name__ == "__main__":
    test_hotkey_manager()
