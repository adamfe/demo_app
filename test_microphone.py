#!/usr/bin/env python3
"""
Test microphone access

This will help diagnose if microphone permissions are granted.
"""

import sounddevice as sd
import numpy as np
import sys

print("=" * 60)
print("Testing Microphone Access")
print("=" * 60)

print("\n1. Checking available audio devices...")
try:
    devices = sd.query_devices()
    print(f"✓ Found {len(devices)} audio devices")

    # Find default input device
    default_input = sd.query_devices(kind='input')
    print(f"\n2. Default input device:")
    print(f"   Name: {default_input['name']}")
    print(f"   Channels: {default_input['max_input_channels']}")
    print(f"   Sample rate: {default_input['default_samplerate']}")

except Exception as e:
    print(f"✗ Error querying devices: {e}")
    sys.exit(1)

print("\n3. Testing microphone recording for 2 seconds...")
print("   (macOS should prompt for permission if not granted)")
print("   Please speak into your microphone...")

try:
    # Record for 2 seconds
    duration = 2  # seconds
    sample_rate = 16000

    print(f"\n   🔴 Recording...")
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()  # Wait until recording is finished
    print(f"   ✓ Recording complete!")

    # Calculate audio level
    max_level = np.max(np.abs(recording))
    rms_level = np.sqrt(np.mean(recording**2))

    print(f"\n4. Audio Analysis:")
    print(f"   Max amplitude: {max_level:.4f}")
    print(f"   RMS level: {rms_level:.4f}")

    if max_level < 0.001:
        print(f"\n⚠️  WARNING: Audio level is very low!")
        print(f"   Possible causes:")
        print(f"   - Microphone permission not granted")
        print(f"   - Microphone is muted")
        print(f"   - Wrong input device selected")
    else:
        print(f"\n✓ SUCCESS: Microphone is working!")
        print(f"   Audio was captured successfully.")

except Exception as e:
    print(f"\n✗ ERROR: Failed to record audio")
    print(f"   {e}")
    print(f"\nThis likely means microphone permission is not granted.")
    print(f"\nTo fix:")
    print(f"1. Open System Settings")
    print(f"2. Go to Privacy & Security → Microphone")
    print(f"3. Enable Terminal (or Python)")
    sys.exit(1)

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
