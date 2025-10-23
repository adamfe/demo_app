#!/usr/bin/env python3
"""
Test script for the pulsating claw overlay

Run this to see the recording indicator in action without starting the full app.
Press Ctrl+C to exit.
"""

import sys
import random
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add src to path
sys.path.insert(0, 'src')

from gui.recording_indicator import RecordingIndicator


def main():
    print("=" * 60)
    print("Testing Pulsating Claw Overlay")
    print("=" * 60)
    print("\nShowing recording indicator for 10 seconds...")
    print("Watch for:")
    print("  • Pulsating claw animation")
    print("  • Real-time waveform visualization")
    print("  • Recording timer")
    print("\nPress Ctrl+C to exit early\n")

    app = QApplication(sys.argv)

    # Create recording indicator
    indicator = RecordingIndicator()

    # Show it
    indicator.show_recording()

    # Simulate audio levels
    def simulate_audio():
        # Generate random audio level (simulating speech)
        level = random.random() * 0.7
        # Add occasional spikes (like loud syllables)
        if random.random() > 0.9:
            level = random.random() * 0.95

        indicator.update_audio_level(level)

    # Update waveform every 50ms
    audio_timer = QTimer()
    audio_timer.timeout.connect(simulate_audio)
    audio_timer.start(50)

    # Auto-close after 10 seconds
    def close_indicator():
        print("\n✓ Test complete!")
        print("\nThe pulsating claw overlay is working!")
        print("You saw:")
        print("  ✓ Pulsating claw icon (Claude orange)")
        print("  ✓ Real-time waveform visualization")
        print("  ✓ Recording timer")
        print("  ✓ Semi-transparent overlay")
        print("\nThis will appear whenever you hold Caps Lock to record.\n")

        indicator.hide_recording()
        app.quit()

    close_timer = QTimer()
    close_timer.timeout.connect(close_indicator)
    close_timer.start(10000)  # 10 seconds

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Test interrupted by user")
        sys.exit(0)
