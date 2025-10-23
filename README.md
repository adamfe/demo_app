# Voice Mode 🎤

**AI-powered voice dictation for macOS with context awareness and Claude refinement**

Voice Mode is a native macOS menu bar app that transforms voice into text using state-of-the-art speech recognition, with optional AI-powered refinement through Claude.

## ✨ Features

- **🎤 Hold-to-Dictate**: Press and hold Caps Lock to record (fully customizable)
- **🧠 Local Whisper**: State-of-the-art speech recognition running entirely on your Mac
- **🔍 Context-Aware**: Captures screen content, browser tabs, and active apps to improve transcription accuracy
- **✨ AI Refinement**: Optional Claude integration to polish your dictation with custom prompts
- **📋 Instant Copy**: Transcribed text goes directly to your clipboard
- **🎨 Visual Feedback**: Pulsating claw icon overlay while recording
- **🔒 Privacy First**: All transcription happens locally on your device
- **⚡ Fast**: Optimized for Apple Silicon (M1/M2/M3)
- **🎯 Flexible**: Swappable models and customizable prompts

## 🎯 Perfect For

- Drafting emails and documents
- Writing code comments
- Taking meeting notes
- Quick text capture
- Voice-to-text anywhere on your Mac

## 🚀 Quick Start

### Requirements

- macOS Sequoia 15.0+ (tested on 15.6.1)
- Python 3.10+
- Apple Silicon recommended (works on Intel too)
- ~3GB disk space for Whisper model

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/voice-mode.git
cd voice-mode

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# (Optional) Add your Claude API key to .env
# ANTHROPIC_API_KEY=sk-ant-...

# Run the app
python src/app.py
```

### First Run

1. **Grant Permissions**: Voice Mode will prompt for:
   - Microphone access
   - Accessibility (for hotkey detection)
   - Screen Recording (for context capture)

2. **Download Model**: The first time you run Voice Mode, it will download the Whisper model (~3GB for medium model)

3. **Configure Hotkey**: Default is Caps Lock. Change in Preferences if needed.

4. **Start Dictating**: Hold your hotkey and speak!

## 📖 Usage

### Basic Dictation

1. Hold **Caps Lock** (or your custom hotkey)
2. Speak clearly into your microphone
3. See the pulsating claw icon 🦞 while recording
4. Release the hotkey when done
5. Text appears in your clipboard
6. Paste anywhere with **⌘V**

### With Claude Refinement

1. Open Preferences (click menu bar icon)
2. Go to **Claude** tab
3. Enable Claude processing
4. Enter your Anthropic API key
5. Choose a processing mode:
   - **Formal Writing**: Professional, polished text
   - **Casual**: Natural, conversational tone
   - **Code Comment**: Technical documentation
   - **Email**: Structured email format
   - **Meeting Notes**: Organized bullets and action items
   - **Custom**: Your own prompt

Now when you dictate, Claude will automatically refine your text!

### Context Awareness

Voice Mode can capture context to improve transcription:

- **Screen Text**: OCR of visible text
- **Browser Tabs**: Open tab titles
- **Active Apps**: Currently running applications
- **Window Title**: Active window name

This context helps Whisper (and optionally Claude) understand domain-specific terms, acronyms, and proper nouns.

Enable/disable in **Preferences → Context**

## ⚙️ Configuration

### Settings Location

- Default settings: `config/default_settings.yaml`
- User settings: `~/Library/Application Support/VoiceMode/settings.yaml`
- Prompts: `config/prompts.yaml`

### Key Settings

```yaml
# Hotkey
hotkey:
  type: "caps_lock"          # or "fn", "option+space", etc.

# Whisper Model
transcription:
  model: "medium"            # tiny, base, small, medium, large-v3
  engine: "whisper"          # whisper, mlx-whisper, whisper-cpp

# Context
context:
  enabled: true
  capture_screen: true
  ocr_enabled: true

# Claude
claude:
  enabled: false             # Toggle AI refinement
  model: "claude-3-5-sonnet-20241022"
  default_mode: "formal"

# UI
ui:
  claw_icon_enabled: true
  claw_pulse_speed: 1.0
  show_waveform: true
```

## 🎨 Customization

### Custom Prompts

Edit `config/prompts.yaml` to create your own Claude prompts:

```yaml
prompts:
  my_custom_prompt:
    name: "My Custom Style"
    description: "Description here"
    system: |
      Your custom system prompt here
    user_template: |
      Transcription: {transcription}
      {context_section}
      Your instructions here
```

### Swapping Models

Change the Whisper model in Settings:

- **tiny**: Fastest, least accurate (~75MB)
- **base**: Fast, decent accuracy (~142MB)
- **small**: Good balance (~466MB)
- **medium**: Recommended (~1.5GB) ⭐
- **large-v3**: Best accuracy, slower (~2.9GB)

Or via CLI:
```bash
python src/utils/models.py download large-v3
```

## 🏗️ Architecture

```
voice-mode/
├── src/
│   ├── app.py                 # Main entry point
│   ├── gui/                   # UI components
│   │   ├── settings_window.py
│   │   └── recording_indicator.py
│   ├── core/                  # Core functionality
│   │   ├── hotkey_manager.py
│   │   ├── audio_recorder.py
│   │   └── whisper_engine.py
│   ├── context/               # Context capture
│   ├── processing/            # Claude integration
│   └── output/                # Clipboard & notifications
├── config/                    # Configuration files
└── resources/                 # Icons and assets
```

## 🔧 Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
pylint src/
```

### Building .app Bundle

```bash
./build_app.sh
```

The packaged app will be in `dist/VoiceMode.app`

## 🐛 Troubleshooting

### Caps Lock not working

Try the fallback hotkey (Option+Space) or:
1. Go to **System Settings → Privacy & Security → Accessibility**
2. Add Voice Mode to the list
3. Restart the app

### Poor transcription quality

- Use a better microphone
- Speak clearly and at a normal pace
- Enable context capture for domain-specific terms
- Try the large-v3 model for best accuracy

### Claude not refining text

- Check your API key in Preferences
- Verify internet connection
- Check API key balance at console.anthropic.com

### High CPU usage

- Switch to a smaller Whisper model (small or tiny)
- Disable live transcription preview
- Disable context capture features you don't need

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [Anthropic Claude](https://www.anthropic.com/claude) - AI refinement
- [rumps](https://github.com/jaredks/rumps) - macOS menu bar framework
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/voice-mode/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/voice-mode/discussions)
- **Email**: your.email@example.com

---

**Made with ❤️ for macOS • Powered by Whisper & Claude**
