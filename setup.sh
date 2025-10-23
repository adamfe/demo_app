#!/bin/bash
# Voice Mode - Setup Script
# Run this on your Mac to set up Voice Mode

set -e  # Exit on error

echo "======================================================================"
echo "Voice Mode - Setup Script"
echo "======================================================================"
echo ""

# Check Python version
echo "1. Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Check macOS version
echo "2. Checking macOS version..."
MACOS_VERSION=$(sw_vers -productVersion)
echo "✓ macOS $MACOS_VERSION"
echo ""

# Create virtual environment
echo "3. Creating virtual environment..."
if [ -d "venv" ]; then
    echo "  Virtual environment already exists, skipping."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "4. Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "5. Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "6. Installing dependencies..."
echo "   This may take 5-10 minutes..."
echo ""
pip install -r requirements.txt
echo ""
echo "✓ Dependencies installed"
echo ""

# Check if Whisper can be imported
echo "7. Verifying Whisper installation..."
python3 -c "import whisper; print('✓ Whisper imported successfully')"
echo ""

# Check PyQt6
echo "8. Verifying PyQt6 installation..."
python3 -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 imported successfully')"
echo ""

# Check sounddevice
echo "9. Verifying audio support..."
python3 -c "import sounddevice; print('✓ Audio support available')"
echo ""

# Create cache directory
echo "10. Creating cache directory..."
mkdir -p ~/.cache/whisper
echo "✓ Cache directory ready"
echo ""

echo "======================================================================"
echo "✓ Setup Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Test the pulsating claw overlay:"
echo "   python3 test_claw_overlay.py"
echo ""
echo "2. Run Voice Mode:"
echo "   python3 src/app.py"
echo ""
echo "   On first run, it will:"
echo "   - Request permissions (Microphone, Accessibility, Screen Recording)"
echo "   - Download Whisper model (~1.5GB, takes 5-10 minutes)"
echo "   - Load model into memory (~10-30 seconds)"
echo "   - Show 🎤 icon in menu bar when ready"
echo ""
echo "3. Use Voice Mode:"
echo "   - Hold Caps Lock to record"
echo "   - Speak clearly"
echo "   - Release Caps Lock to transcribe"
echo "   - Text appears in clipboard!"
echo ""
echo "For detailed testing instructions, see TESTING.md"
echo ""
echo "Have fun! 🎉"
echo ""
