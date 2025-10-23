# Voice Mode - Testing Guide

Complete guide for testing Voice Mode on macOS.

## Prerequisites

- macOS Sequoia 15.0+ (you have 15.6.1 ✓)
- Python 3.10 or higher
- About 2GB free disk space (for Whisper model)
- Working microphone

## Step 1: Install Dependencies

```bash
cd ~/demo_app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies (this takes 5-10 minutes)
pip install -r requirements.txt
```

**Expected output:**
- All packages install successfully
- No major errors (some warnings are OK)

## Step 2: Test Individual Components

Before running the full app, test components individually:

### 2.1 Test Configuration System

```bash
python3 -c "from src.utils.config import get_config; config = get_config(); print('✓ Config loaded'); print(f'Model: {config.get(\"transcription.model\")}')"
```

**Expected:** `✓ Config loaded` and `Model: medium`

### 2.2 Test Permissions Checker

```bash
python3 src/utils/permissions.py
```

**Expected:**
- Shows status of all permissions
- Lists which are granted/not granted
- May prompt to open System Settings

### 2.3 Test Audio Recorder

```bash
python3 src/core/audio_recorder.py
```

**Expected:**
- Lists available audio devices
- Records 3 seconds of audio
- Shows audio level bars in real-time
- No errors

### 2.4 Test Whisper Engine (Downloads Model!)

```bash
python3 src/core/whisper_engine.py
```

**Expected:**
- Downloads tiny model (~75MB) if not cached
- Shows model info
- Attempts transcription (may not work on sine wave, that's OK)
- **This will take 1-2 minutes on first run**

### 2.5 Test Model Manager

```bash
python3 src/utils/model_manager.py
```

**Expected:**
- Shows all available models
- Shows which are downloaded
- Shows cache size

### 2.6 Test Recording Indicator (Pulsating Claw!)

```bash
python3 test_claw_overlay.py
```

**Expected:**
- Beautiful overlay window appears in center of screen
- Pulsating claw icon with orange glow
- Real-time waveform animation
- Timer counts up
- Auto-closes after 10 seconds
- **This is what you'll see when recording!**

## Step 3: Run Voice Mode (Full App)

### First Run (Long - downloads model)

```bash
python3 src/app.py
```

**What happens:**

1. **Permission Check** (~10 seconds)
   - May open System Settings
   - Grant: Microphone, Accessibility, Screen Recording
   - Close System Settings and return to terminal

2. **Initialization** (~1 minute on first run, ~10 seconds after)
   - Qt application starts
   - Menu bar icon 🎤 appears in top-right
   - Downloads medium model (~1.5GB) - **THIS TAKES 5-10 MINUTES**
   - Progress shown in terminal and menu bar
   - Loads model into memory (~10-30 seconds)

3. **Ready State**
   - Menu bar icon: 🎤
   - Menu status: "● Ready to dictate"
   - Terminal shows: "✓ Voice Mode initialized successfully"

**If first run takes too long**, you can edit `config/default_settings.yaml` to use a smaller model:

```yaml
transcription:
  model: "tiny"  # Change from "medium" to "tiny" (only 75MB)
```

## Step 4: Test Dictation

### Test 1: Basic Dictation

1. **Start Recording**: Hold **Caps Lock**
   - Pulsating claw overlay appears 🦞
   - Waveform shows audio levels
   - Timer starts: 0:00, 0:01, 0:02...

2. **Speak**: "Hello world, this is a test of voice mode."

3. **Stop Recording**: Release **Caps Lock**
   - Overlay disappears
   - Menu bar icon: ⏳ "Transcribing..."
   - Processing takes 1-5 seconds

4. **Check Result**:
   - macOS notification appears with transcribed text
   - Text is in clipboard
   - Open any app (TextEdit, Notes, etc.)
   - Press ⌘V to paste
   - **Expected:** "Hello world, this is a test of voice mode."

### Test 2: Longer Dictation

1. Hold Caps Lock
2. Speak for 10-15 seconds about anything
3. Release Caps Lock
4. Check clipboard - should have full transcription

### Test 3: Multiple Languages (if applicable)

The model auto-detects language. Try speaking in different languages!

### Test 4: Punctuation and Complex Sentences

Try: "Hello, my name is [Your Name]. I'm testing Voice Mode on macOS. It's working great! How are you?"

### Test 5: Technical Terms

Try: "I'm using Python, Whisper, and Claude to build an AI-powered voice dictation app."

## Step 5: Test Menu Bar Features

1. **Click menu bar icon** 🎤
2. Try each menu item:
   - ✓ Shows current status
   - ✓ Preferences (shows placeholder dialog)
   - ✓ Help (shows help text)
   - ✓ Pause Voice Mode (disables hotkey)
   - ✓ Resume Voice Mode
   - ✓ Quit Voice Mode (closes app)

## Common Issues & Solutions

### Issue: "Model not found" or download fails

**Solution:**
```bash
# Manually download model
python3 -c "import whisper; whisper.load_model('medium')"
```

### Issue: Caps Lock not working

**Solution 1:** Try fallback hotkey
```yaml
# Edit config/default_settings.yaml
hotkey:
  type: "option+space"  # Instead of caps_lock
```

**Solution 2:** Check Accessibility permission
- System Settings → Privacy & Security → Accessibility
- Add Terminal or Python to the list

### Issue: No audio / "Audio device not found"

**Solution:**
```bash
# List available devices
python3 -c "import sounddevice as sd; print(sd.query_devices())"

# Test system microphone
python3 -c "import sounddevice as sd; import numpy as np; print('Recording...'); audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1); sd.wait(); print('Done')"
```

### Issue: Transcription is empty or wrong

**Possible causes:**
- Audio too short (speak for at least 1 second)
- Microphone level too low (check System Settings → Sound)
- Background noise too loud
- Speaking too fast or unclear

**Solution:**
- Speak clearly and at moderate pace
- Use a better microphone if available
- Try a larger model (large-v3) for better accuracy

### Issue: App crashes or freezes

**Solution:**
```bash
# Check terminal for error messages
# Try smaller model first:
# Edit config/default_settings.yaml → model: "tiny"
# Restart app
```

### Issue: High CPU usage

**Expected behavior:**
- ~5-10% CPU when idle
- ~50-100% CPU during transcription (normal!)
- Drops back to idle after transcription

If CPU stays high:
- Try smaller model (tiny or small)
- Close other apps

## Performance Benchmarks

**Transcription Speed** (approximate):

| Model | 3 sec audio | 10 sec audio | 30 sec audio |
|-------|-------------|--------------|--------------|
| tiny | ~0.5s | ~1s | ~3s |
| small | ~1s | ~2s | ~5s |
| medium | ~2s | ~4s | ~10s |
| large-v3 | ~3s | ~6s | ~15s |

**Memory Usage:**

| Model | RAM Usage |
|-------|-----------|
| tiny | ~400 MB |
| small | ~800 MB |
| medium | ~1.5 GB |
| large-v3 | ~3 GB |

## Success Criteria

✅ **Core Functionality:**
- [ ] App starts without errors
- [ ] Menu bar icon appears
- [ ] Caps Lock triggers recording
- [ ] Pulsating claw overlay appears
- [ ] Waveform shows audio in real-time
- [ ] Recording stops when Caps Lock released
- [ ] Transcription completes within 5 seconds
- [ ] Text copied to clipboard
- [ ] Notification shows transcribed text
- [ ] Text is accurate (>90% for clear speech)

✅ **Polish:**
- [ ] Overlay looks good (smooth animation)
- [ ] No lag or stuttering
- [ ] Menu bar responsive
- [ ] Clean quit (no hanging processes)

✅ **Edge Cases:**
- [ ] Very short recording (1 second)
- [ ] Long recording (30+ seconds)
- [ ] Rapid repeated recordings
- [ ] Pause and resume works
- [ ] App survives bad audio input

## Next Steps After Testing

Once testing is complete, report:

1. **What worked?**
   - Which features work perfectly
   - Any pleasant surprises

2. **What didn't work?**
   - Errors or crashes
   - Unexpected behavior
   - Performance issues

3. **What would you change?**
   - UX improvements
   - Feature requests
   - Configuration options

4. **Ready for next phase?**
   - Context awareness (Phase 3)
   - Claude integration (Phase 4)
   - Settings GUI (Phase 5)

---

## Quick Test Checklist

```bash
# 1. Install
pip install -r requirements.txt

# 2. Test components
python3 test_claw_overlay.py  # See the claw!

# 3. Run app
python3 src/app.py

# 4. Use it
# Hold Caps Lock → Speak → Release → Paste!

# 5. Report back!
```

**Have fun testing! 🎉**
