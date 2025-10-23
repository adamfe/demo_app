#!/usr/bin/env python3
"""
Voice Mode - Diagnostic Tool

Run this to diagnose issues with Voice Mode setup.
"""

import sys
import subprocess
from pathlib import Path

def check(name, test_func):
    """Run a test and report result"""
    try:
        result = test_func()
        if result:
            print(f"✓ {name}: {result}")
        else:
            print(f"✓ {name}")
        return True
    except Exception as e:
        print(f"✗ {name}: {e}")
        return False

def main():
    print("=" * 60)
    print("Voice Mode - Diagnostic Tool")
    print("=" * 60)
    print()

    results = []

    # Python version
    print("1. Python Environment")
    print("-" * 60)
    results.append(check(
        "Python version",
        lambda: f"{sys.version.split()[0]}"
    ))
    results.append(check(
        "Python executable",
        lambda: sys.executable
    ))
    print()

    # Import core dependencies
    print("2. Core Dependencies")
    print("-" * 60)

    results.append(check(
        "numpy",
        lambda: __import__('numpy').__version__
    ))

    results.append(check(
        "torch",
        lambda: __import__('torch').__version__
    ))

    results.append(check(
        "whisper",
        lambda: __import__('whisper').__version__
    ))

    results.append(check(
        "sounddevice",
        lambda: __import__('sounddevice').__version__
    ))

    results.append(check(
        "PyQt6",
        lambda: __import__('PyQt6.QtCore').QtCore.qVersion()
    ))

    results.append(check(
        "rumps",
        lambda: __import__('rumps').__version__
    ))

    results.append(check(
        "anthropic",
        lambda: __import__('anthropic').__version__
    ))

    results.append(check(
        "pynput",
        lambda: __import__('pynput').__version__
    ))

    print()

    # Check audio devices
    print("3. Audio System")
    print("-" * 60)
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = [d for d in devices if d.get('max_input_channels', 0) > 0]
        print(f"✓ Found {len(input_devices)} input device(s):")
        for i, device in enumerate(input_devices[:3]):  # Show first 3
            print(f"  [{i}] {device['name']}")
        if len(input_devices) > 3:
            print(f"  ... and {len(input_devices) - 3} more")
        results.append(True)
    except Exception as e:
        print(f"✗ Audio devices: {e}")
        results.append(False)
    print()

    # Check Whisper model cache
    print("4. Whisper Models")
    print("-" * 60)
    cache_dir = Path.home() / ".cache" / "whisper"
    if cache_dir.exists():
        models = list(cache_dir.glob("*.pt"))
        if models:
            print(f"✓ Found {len(models)} cached model(s):")
            for model in models:
                size_mb = model.stat().st_size / (1024 * 1024)
                print(f"  {model.name}: {size_mb:.1f}MB")
            results.append(True)
        else:
            print("○ No models cached yet (will download on first run)")
            results.append(True)
    else:
        print("○ Cache directory not created yet")
        results.append(True)
    print()

    # Check Voice Mode files
    print("5. Voice Mode Files")
    print("-" * 60)
    required_files = [
        "src/app.py",
        "src/core/whisper_engine.py",
        "src/core/audio_recorder.py",
        "src/core/hotkey_manager.py",
        "src/gui/recording_indicator.py",
        "config/default_settings.yaml",
        "config/prompts.yaml",
    ]

    all_exist = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} (missing)")
            all_exist = False
    results.append(all_exist)
    print()

    # Check PyObjC (macOS specific)
    print("6. macOS Integration")
    print("-" * 60)
    try:
        from Cocoa import NSApplication
        print("✓ PyObjC (Cocoa)")
        results.append(True)
    except Exception as e:
        print(f"○ PyObjC: {e}")
        print("  (This is normal if not on macOS)")
        results.append(True)  # Don't fail on non-macOS

    try:
        from Quartz import CGWindowListCreateImage
        print("✓ Quartz (Screen capture)")
        results.append(True)
    except Exception as e:
        print(f"○ Quartz: {e}")
        print("  (This is normal if not on macOS)")
        results.append(True)

    print()

    # Check torch device
    print("7. Acceleration")
    print("-" * 60)
    try:
        import torch
        if torch.backends.mps.is_available():
            print("✓ Apple Silicon (MPS) available - Fast transcription!")
            results.append(True)
        elif torch.cuda.is_available():
            print("✓ CUDA available")
            results.append(True)
        else:
            print("○ CPU only (slower transcription)")
            print("  Consider using smaller models (tiny, small)")
            results.append(True)
    except Exception as e:
        print(f"✗ Torch device check: {e}")
        results.append(False)
    print()

    # Summary
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} checks passed")
    print("=" * 60)
    print()

    if passed == total:
        print("✓ All checks passed! Voice Mode should work.")
        print()
        print("Next steps:")
        print("  1. Test the overlay: python3 test_claw_overlay.py")
        print("  2. Run Voice Mode: python3 src/app.py")
    elif passed >= total * 0.8:
        print("⚠ Most checks passed. Voice Mode might work with issues.")
        print()
        print("Try running anyway:")
        print("  python3 src/app.py")
    else:
        print("✗ Several checks failed. Please fix issues before running.")
        print()
        print("Common fixes:")
        print("  - Reinstall dependencies: pip install -r requirements.txt")
        print("  - Check Python version: python3 --version (need 3.10+)")
        print("  - Make sure you're on macOS")
    print()


if __name__ == "__main__":
    main()
