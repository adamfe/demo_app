# Voice Mode - Quick Start

Get Voice Mode running in 5 minutes!

## TL;DR

```bash
# 1. Install (5-10 minutes)
./setup.sh

# 2. Test the claw overlay (30 seconds)
python3 test_claw_overlay.py

# 3. Run Voice Mode (first run: 10-15 minutes for model download)
python3 src/app.py

# 4. Use it!
# Hold Caps Lock → Speak → Release → Paste!
```

---

## Detailed Steps

### Step 1: Install Dependencies (5-10 minutes)

```bash
cd ~/demo_app
./setup.sh
```

This will:
- Create a virtual environment
- Install all Python packages
- Verify everything works

**Expected:** All checks pass with ✓

---

### Step 2: Test the Pulsating Claw (30 seconds)

```bash
python3 test_claw_overlay.py
```

You should see:
- 🦞 Orange pulsating claw icon in center of screen
- Real-time waveform animation
- Recording timer
- Semi-transparent dark overlay

**This is what appears when you record!**

---

### Step 3: Run Voice Mode (10-15 minutes first time)

```bash
python3 src/app.py
```

#### First Run Only:

1. **Grant Permissions** (2 minutes)
   - System Settings will open
   - Grant: Microphone ✓
   - Grant: Accessibility ✓
   - Grant: Screen Recording ✓
   - Close System Settings

2. **Download Model** (5-10 minutes)
   - Downloads Whisper medium model (~1.5GB)
   - Progress shown in terminal
   - **This only happens once!**

3. **Load Model** (30 seconds)
   - Loads model into memory
   - Terminal shows: "✓ Voice Mode initialized successfully"

4. **Ready!**
   - 🎤 icon appears in menu bar
   - Status shows: "● Ready to dictate"

#### Subsequent Runs:
- Only takes ~10 seconds (model already downloaded!)

---

### Step 4: Test Dictation!

#### Your First Dictation:

1. **Hold Caps Lock**
   - Pulsating claw 🦞 appears
   - Waveform shows your voice

2. **Say**: "Hello world, this is my first test of Voice Mode"

3. **Release Caps Lock**
   - Overlay disappears
   - Menu bar shows "⏳ Transcribing..."
   - Takes ~2 seconds

4. **Check Result**:
   - macOS notification with your text
   - Text automatically in clipboard
   - Open any app (Notes, TextEdit, etc.)
   - Press **⌘V** to paste

5. **Success! 🎉**

---

## Quick Troubleshooting

### "Model download is slow"

**Normal!** The medium model is 1.5GB. On a slow connection, use a smaller model:

```bash
# Edit config/default_settings.yaml
transcription:
  model: "tiny"  # Only 75MB, downloads in 30 seconds
```

### "Caps Lock not working"

Try the fallback hotkey:

```bash
# Edit config/default_settings.yaml
hotkey:
  type: "option+space"  # Instead of caps_lock
```

Then restart the app.

### "Permission denied" errors

Make sure you granted all permissions in System Settings:
- Microphone
- Accessibility
- Screen Recording

### "No audio input"

Check your microphone:
```bash
# Test microphone
python3 src/core/audio_recorder.py
```

---

## What's Next?

Once basic testing works:

### Option A: Test More Features
- Try different languages (auto-detected)
- Test with technical terms
- Try longer recordings (30+ seconds)
- Test rapid repeated recordings

### Option B: Add Context Awareness
- Screen capture for better transcription
- OCR to read visible text
- Browser tab detection
- Improves accuracy with domain-specific terms

### Option C: Add Claude Integration
- Refine transcriptions with AI
- Multiple modes: formal, casual, code, email
- Makes your dictation sound professional
- Requires Anthropic API key

### Option D: Build Settings GUI
- Easy configuration (no YAML editing)
- Model selection with visual picker
- Hotkey customization
- Visual preferences

---

## File Structure

```
demo_app/
├── src/
│   ├── app.py                    # Main application ⭐
│   ├── core/
│   │   ├── whisper_engine.py     # Speech-to-text
│   │   ├── audio_recorder.py     # Microphone capture
│   │   └── hotkey_manager.py     # Caps Lock detection
│   ├── gui/
│   │   └── recording_indicator.py # Pulsating claw 🦞
│   └── utils/
│       ├── config.py             # Configuration
│       └── permissions.py        # macOS permissions
├── config/
│   ├── default_settings.yaml     # Settings ⚙️
│   └── prompts.yaml              # Claude prompts
├── test_claw_overlay.py          # Test overlay ✓
├── setup.sh                      # Installation script
├── diagnose.py                   # Diagnostic tool
├── TESTING.md                    # Full testing guide 📖
└── README.md                     # Project documentation
```

---

## Performance

**Transcription Speed** (approximate):

| Audio Length | Transcription Time (medium model) |
|--------------|-----------------------------------|
| 3 seconds | ~2 seconds |
| 10 seconds | ~4 seconds |
| 30 seconds | ~10 seconds |

**Accuracy**: 90-95% for clear English speech

**Resource Usage**:
- RAM: ~1.5GB (medium model)
- CPU: ~50-100% during transcription (normal!)
- Disk: ~1.5GB for cached model

---

## Need Help?

1. **Run diagnostics**:
   ```bash
   python3 diagnose.py
   ```

2. **Check detailed guide**:
   - See `TESTING.md` for comprehensive instructions
   - See `README.md` for project documentation

3. **Report issues**:
   - Include output from `diagnose.py`
   - Describe what you were doing
   - Copy error messages from terminal

---

## Success Checklist

After testing, you should have:

- ✅ Installed all dependencies
- ✅ Seen the pulsating claw overlay
- ✅ Successfully transcribed at least one recording
- ✅ Pasted transcribed text somewhere
- ✅ Smiled because it worked! 😊

**Happy dictating! 🎤🦞**
