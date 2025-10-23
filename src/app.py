"""
Voice Mode - Main Application

macOS menu bar app for AI-powered voice dictation with context awareness.
"""

import rumps
import threading
import numpy as np
from pathlib import Path
from typing import Optional

from core.state_machine import StateMachine, AppState
from core.hotkey_manager import HotkeyManager
from core.audio_recorder import AudioRecorder
from utils.config import get_config
from utils.permissions import check_and_request_permissions, Permission


class VoiceModeApp(rumps.App):
    """
    Main Voice Mode application

    A menu bar app that provides voice-to-text dictation with:
    - Hold-to-dictate with Caps Lock
    - Local Whisper transcription
    - Optional Claude refinement
    - Context awareness
    """

    def __init__(self):
        # Initialize rumps app
        super(VoiceModeApp, self).__init__(
            name="Voice Mode",
            title="🎤",  # Menu bar icon (will use PNG later)
            quit_button=None  # We'll add custom quit
        )

        # Load configuration
        self.config = get_config()

        # State management
        self.state_machine = StateMachine()

        # Components (will be initialized later)
        self.hotkey_manager: Optional[HotkeyManager] = None
        self.audio_recorder: Optional[AudioRecorder] = None
        self.current_audio: Optional[np.ndarray] = None

        # Recording indicator (GUI window - will implement later)
        self.recording_indicator = None

        # Setup menu
        self._setup_menu()

        # Register state callbacks
        self._setup_state_callbacks()

    def _setup_menu(self):
        """Setup menu bar dropdown menu"""
        # Status item (shows current state)
        self.menu_status = rumps.MenuItem(
            title="● Ready to dictate",
            callback=None  # Non-clickable status
        )

        # Separator
        self.menu_separator1 = rumps.separator

        # Preferences
        self.menu_preferences = rumps.MenuItem(
            title="⚙️  Preferences...",
            callback=self.show_preferences
        )

        # Help
        self.menu_help = rumps.MenuItem(
            title="❓ Help",
            callback=self.show_help
        )

        # Separator
        self.menu_separator2 = rumps.separator

        # Pause/Resume
        self.menu_pause = rumps.MenuItem(
            title="🔇 Pause Voice Mode",
            callback=self.toggle_pause
        )

        # Launch at login
        self.menu_launch_at_login = rumps.MenuItem(
            title="🚀 Launch at Login",
            callback=self.toggle_launch_at_login
        )
        # Set checkmark based on config
        if self.config.get("general.launch_at_login", False):
            self.menu_launch_at_login.state = True

        # Separator
        self.menu_separator3 = rumps.separator

        # Quit
        self.menu_quit = rumps.MenuItem(
            title="Quit Voice Mode",
            callback=self.quit_app
        )

        # Build menu
        self.menu = [
            self.menu_status,
            self.menu_separator1,
            self.menu_preferences,
            self.menu_help,
            self.menu_separator2,
            self.menu_pause,
            self.menu_launch_at_login,
            self.menu_separator3,
            self.menu_quit
        ]

    def _setup_state_callbacks(self):
        """Register callbacks for state transitions"""
        self.state_machine.register_callback(
            AppState.IDLE,
            on_enter=self._on_idle
        )
        self.state_machine.register_callback(
            AppState.RECORDING,
            on_enter=self._on_recording_start,
            on_exit=self._on_recording_stop
        )
        self.state_machine.register_callback(
            AppState.PROCESSING,
            on_enter=self._on_processing
        )
        self.state_machine.register_callback(
            AppState.ERROR,
            on_enter=self._on_error
        )

    def _on_idle(self, **kwargs):
        """Called when entering IDLE state"""
        self.title = "🎤"  # Gray microphone
        hotkey_desc = self.hotkey_manager.get_hotkey_description() if self.hotkey_manager else "Hold Caps Lock"
        self.menu_status.title = f"● Ready to dictate\n   {hotkey_desc} to record"

    def _on_recording_start(self, **kwargs):
        """Called when starting recording"""
        self.title = "🔴"  # Red dot (will add pulsing animation later)
        self.menu_status.title = "🔴 Recording..."

        # Show recording indicator (pulsating claw - implement later)
        # TODO: Show pulsating claw overlay

    def _on_recording_stop(self):
        """Called when stopping recording"""
        # Hide recording indicator
        # TODO: Hide pulsating claw overlay
        pass

    def _on_processing(self, **kwargs):
        """Called when starting transcription"""
        self.title = "⏳"  # Hourglass
        self.menu_status.title = "⏳ Transcribing..."

    def _on_error(self, **kwargs):
        """Called when error occurs"""
        self.title = "⚠️"
        error_msg = kwargs.get('error', 'Unknown error')
        self.menu_status.title = f"⚠️  Error: {error_msg}"

        # Show notification
        rumps.notification(
            title="Voice Mode Error",
            subtitle="An error occurred",
            message=str(error_msg)
        )

    def _on_start_recording(self):
        """Callback when hotkey pressed (start recording)"""
        if not self.state_machine.is_ready():
            print("Cannot start recording - app not ready")
            return

        # Transition to recording state
        if self.state_machine.transition_to(AppState.RECORDING):
            # Start audio recording
            if self.audio_recorder:
                self.audio_recorder.start_recording()

    def _on_stop_recording(self):
        """Callback when hotkey released (stop recording)"""
        if not self.state_machine.is_state(AppState.RECORDING):
            return

        # Stop audio recording
        if self.audio_recorder:
            self.current_audio = self.audio_recorder.stop_recording()

        # Transition to processing
        if self.current_audio is not None:
            self.state_machine.transition_to(AppState.PROCESSING)

            # Process in background thread
            threading.Thread(
                target=self._process_audio,
                daemon=True
            ).start()
        else:
            # No audio recorded, return to idle
            self.state_machine.transition_to(AppState.IDLE)

    def _process_audio(self):
        """Process recorded audio (transcription + optional Claude)"""
        try:
            # TODO: Implement Whisper transcription
            # For now, just simulate processing
            import time
            time.sleep(2)  # Simulate processing

            # Placeholder transcription
            transcription = "[Transcription will be implemented in next phase]"

            # Transition to copying
            self.state_machine.transition_to(AppState.COPYING)

            # Copy to clipboard
            self._copy_to_clipboard(transcription)

            # Return to idle
            self.state_machine.transition_to(AppState.IDLE)

            # Show notification
            rumps.notification(
                title="Voice Mode",
                subtitle="Text copied to clipboard",
                message=transcription[:100] + ("..." if len(transcription) > 100 else "")
            )

        except Exception as e:
            self.state_machine.transition_to(AppState.ERROR, error=str(e))

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        import subprocess
        try:
            process = subprocess.Popen(
                ['pbcopy'],
                stdin=subprocess.PIPE
            )
            process.communicate(text.encode('utf-8'))
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            raise

    def show_preferences(self, _):
        """Show preferences window"""
        # TODO: Implement PyQt6 preferences window
        rumps.alert(
            title="Preferences",
            message="Preferences window coming soon!\n\nFor now, edit:\n~/Library/Application Support/VoiceMode/settings.yaml"
        )

    def show_help(self, _):
        """Show help dialog"""
        help_text = """Voice Mode - AI-Powered Dictation

How to use:
1. Hold Caps Lock to start recording
2. Speak clearly
3. Release Caps Lock when done
4. Text will be copied to clipboard

Features:
• Local Whisper transcription
• Optional Claude refinement
• Context-aware dictation

For more help, visit:
github.com/yourusername/voice-mode
"""
        rumps.alert(
            title="Voice Mode Help",
            message=help_text
        )

    def toggle_pause(self, sender):
        """Pause/resume voice mode"""
        if self.state_machine.is_state(AppState.PAUSED):
            # Resume
            self.state_machine.transition_to(AppState.IDLE)
            sender.title = "🔇 Pause Voice Mode"
            if self.hotkey_manager:
                self.hotkey_manager.start()
        else:
            # Pause
            self.state_machine.transition_to(AppState.PAUSED)
            sender.title = "▶️  Resume Voice Mode"
            if self.hotkey_manager:
                self.hotkey_manager.stop()

    def toggle_launch_at_login(self, sender):
        """Toggle launch at login"""
        sender.state = not sender.state
        self.config.set("general.launch_at_login", sender.state)

        # TODO: Actually implement launch at login using LaunchAgents
        rumps.notification(
            title="Voice Mode",
            subtitle="Launch at Login",
            message=f"{'Enabled' if sender.state else 'Disabled'} (implementation coming soon)"
        )

    def quit_app(self, _):
        """Quit the application"""
        # Cleanup
        if self.hotkey_manager:
            self.hotkey_manager.stop()

        if self.audio_recorder and self.audio_recorder.is_recording:
            self.audio_recorder.stop_recording()

        # Quit
        rumps.quit_application()

    def initialize_components(self):
        """Initialize all components after checking permissions"""
        try:
            # Initialize hotkey manager
            hotkey_type = self.config.get("hotkey.type", "caps_lock")
            self.hotkey_manager = HotkeyManager(hotkey_type=hotkey_type)
            self.hotkey_manager.set_callbacks(
                on_start=self._on_start_recording,
                on_stop=self._on_stop_recording
            )
            self.hotkey_manager.start()

            # Initialize audio recorder
            self.audio_recorder = AudioRecorder(
                sample_rate=self.config.get("audio.sample_rate", 16000),
                channels=self.config.get("audio.channels", 1),
                dtype=self.config.get("audio.dtype", "float32"),
                blocksize=self.config.get("audio.blocksize", 1024),
                device=self.config.get("audio.input_device")
            )

            # Transition to IDLE (ready)
            self.state_machine.transition_to(AppState.IDLE)

            print("✓ Voice Mode initialized successfully")

        except Exception as e:
            print(f"✗ Error initializing components: {e}")
            self.state_machine.transition_to(AppState.ERROR, error=str(e))


def main():
    """Main entry point"""
    print("=" * 60)
    print("Voice Mode - AI-Powered Voice Dictation")
    print("=" * 60)

    # Check permissions first
    print("\nChecking macOS permissions...")
    all_granted, missing = check_and_request_permissions(interactive=True)

    if not all_granted:
        print("\n⚠️  Some permissions are missing:")
        for perm in missing:
            print(f"   - {perm.value}")
        print("\nVoice Mode may not work correctly without these permissions.")
        print("Please grant them in System Settings and restart the app.\n")

        # Show alert
        rumps.alert(
            title="Permissions Required",
            message=f"Voice Mode needs additional permissions:\n\n" +
                   "\n".join([f"• {p.value}" for p in missing]) +
                   "\n\nPlease grant these in System Settings."
        )

    # Create and run app
    print("\nStarting Voice Mode...")
    app = VoiceModeApp()

    # Initialize components in background thread
    # (so it doesn't block the app startup)
    def init_thread():
        import time
        time.sleep(1)  # Give app time to start
        app.initialize_components()

    threading.Thread(target=init_thread, daemon=True).start()

    # Run app
    app.run()


if __name__ == "__main__":
    main()
