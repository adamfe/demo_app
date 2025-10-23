"""
Whisper Transcription Engine

Handles speech-to-text transcription using OpenAI's Whisper model.
Supports multiple model sizes and swappable backends.
"""

import numpy as np
import whisper
import torch
from typing import Optional, Dict, Callable
from pathlib import Path
from enum import Enum
import warnings

# Suppress FP16 warning on CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")


class WhisperModel(Enum):
    """Available Whisper models"""
    TINY = "tiny"           # ~75 MB, fastest
    BASE = "base"           # ~142 MB, fast
    SMALL = "small"         # ~466 MB, good
    MEDIUM = "medium"       # ~1.5 GB, better
    LARGE_V2 = "large-v2"   # ~2.9 GB, best (older)
    LARGE_V3 = "large-v3"   # ~2.9 GB, best (newest)


class WhisperEngine:
    """
    Whisper transcription engine with model management

    Features:
    - Multiple model sizes (tiny → large-v3)
    - Automatic model downloading
    - GPU acceleration (Metal on Mac)
    - Progress callbacks
    - Context injection for better accuracy
    """

    def __init__(
        self,
        model_name: str = "medium",
        device: Optional[str] = None,
        download_root: Optional[str] = None
    ):
        """
        Initialize Whisper engine

        Args:
            model_name: Model size (tiny, base, small, medium, large-v2, large-v3)
            device: Device to use (None = auto-detect, "cpu", "cuda", "mps")
            download_root: Directory to store models (default: ~/.cache/whisper)
        """
        self.model_name = model_name
        self.model: Optional[whisper.Whisper] = None
        self.device = device or self._get_best_device()
        self.download_root = download_root

        # Progress callback
        self.on_progress: Optional[Callable[[str, float], None]] = None

        print(f"Whisper engine initialized (model: {model_name}, device: {self.device})")

    def _get_best_device(self) -> str:
        """
        Automatically detect the best available device

        Returns:
            Device name: "cuda" (NVIDIA GPU) or "cpu"

        Note: MPS (Apple Silicon) is not used because Whisper uses sparse tensors
        which are not yet supported by PyTorch's MPS backend. Using CPU instead.
        """
        # MPS has issues with sparse tensors used by Whisper
        # Force CPU for now until PyTorch MPS supports sparse operations
        if torch.backends.mps.is_available():
            print("Note: Apple Silicon (MPS) detected but using CPU")
            print("      (MPS doesn't support Whisper's sparse tensors yet)")
            return "cpu"  # Force CPU even on Apple Silicon
        elif torch.cuda.is_available():
            return "cuda"  # NVIDIA GPU
        else:
            return "cpu"

    def load_model(self) -> bool:
        """
        Load the Whisper model (downloads if needed)

        Returns:
            True if model loaded successfully
        """
        try:
            print(f"Loading Whisper model '{self.model_name}'...")

            if self.on_progress:
                self.on_progress("Loading model...", 0.0)

            # Load model (this will download if not cached)
            self.model = whisper.load_model(
                self.model_name,
                device=self.device,
                download_root=self.download_root
            )

            if self.on_progress:
                self.on_progress("Model loaded", 1.0)

            print(f"✓ Model '{self.model_name}' loaded successfully")
            return True

        except Exception as e:
            print(f"✗ Error loading model: {e}")
            if self.on_progress:
                self.on_progress(f"Error: {e}", 0.0)
            return False

    def transcribe(
        self,
        audio: np.ndarray,
        language: Optional[str] = None,
        initial_prompt: Optional[str] = None,
        temperature: float = 0.0,
        **kwargs
    ) -> Dict:
        """
        Transcribe audio to text

        Args:
            audio: Audio data as numpy array (16kHz mono)
            language: Language code (None = auto-detect, "en", "es", etc.)
            initial_prompt: Context to guide transcription
            temperature: Sampling temperature (0 = deterministic)
            **kwargs: Additional Whisper parameters

        Returns:
            Dictionary with keys:
                - text: Transcribed text
                - language: Detected/specified language
                - segments: List of segments with timestamps
                - duration: Audio duration in seconds
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        try:
            if self.on_progress:
                self.on_progress("Transcribing...", 0.0)

            # Ensure audio is the right format
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)

            # Normalize audio to [-1, 1]
            if audio.max() > 1.0 or audio.min() < -1.0:
                audio = audio / np.abs(audio).max()

            # Flatten if stereo (should already be mono from recorder)
            if len(audio.shape) > 1:
                audio = audio.mean(axis=1)

            # Transcribe
            result = self.model.transcribe(
                audio,
                language=language,
                initial_prompt=initial_prompt,
                temperature=temperature,
                fp16=(self.device != "cpu"),  # Use FP16 on GPU/MPS
                **kwargs
            )

            if self.on_progress:
                self.on_progress("Transcription complete", 1.0)

            # Calculate duration
            duration = len(audio) / 16000.0  # Assuming 16kHz

            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "duration": duration
            }

        except Exception as e:
            print(f"✗ Transcription error: {e}")
            if self.on_progress:
                self.on_progress(f"Error: {e}", 0.0)
            raise

    def transcribe_with_context(
        self,
        audio: np.ndarray,
        context: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict:
        """
        Transcribe with context injection

        Context helps Whisper recognize domain-specific terms, names, etc.

        Args:
            audio: Audio data
            context: Context dictionary with keys like:
                - active_app: Name of active application
                - window_title: Window title
                - screen_text: Text visible on screen
                - custom_terms: List of domain-specific terms
            **kwargs: Additional transcribe parameters

        Returns:
            Transcription result dictionary
        """
        # Build initial prompt from context
        initial_prompt = kwargs.pop("initial_prompt", "")

        if context:
            prompt_parts = []

            if context.get("active_app"):
                prompt_parts.append(f"Using {context['active_app']}")

            if context.get("custom_terms"):
                terms = context["custom_terms"]
                if isinstance(terms, list):
                    terms = ", ".join(terms)
                prompt_parts.append(f"Terms: {terms}")

            if prompt_parts:
                context_prompt = ". ".join(prompt_parts) + "."
                initial_prompt = context_prompt + " " + initial_prompt if initial_prompt else context_prompt

        return self.transcribe(
            audio,
            initial_prompt=initial_prompt if initial_prompt else None,
            **kwargs
        )

    def change_model(self, model_name: str) -> bool:
        """
        Switch to a different Whisper model

        Args:
            model_name: New model name

        Returns:
            True if model changed successfully
        """
        if model_name == self.model_name:
            print(f"Already using model '{model_name}'")
            return True

        print(f"Switching from '{self.model_name}' to '{model_name}'...")

        # Unload current model
        if self.model is not None:
            del self.model
            self.model = None

            # Clear GPU cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            elif torch.backends.mps.is_available():
                torch.mps.empty_cache()

        # Update model name and load new model
        self.model_name = model_name
        return self.load_model()

    def get_model_info(self) -> Dict:
        """
        Get information about current model

        Returns:
            Dictionary with model info
        """
        model_sizes = {
            "tiny": {"size_mb": 75, "params": "39M", "speed": "~10x"},
            "base": {"size_mb": 142, "params": "74M", "speed": "~7x"},
            "small": {"size_mb": 466, "params": "244M", "speed": "~4x"},
            "medium": {"size_mb": 1500, "params": "769M", "speed": "~2x"},
            "large-v2": {"size_mb": 2900, "params": "1550M", "speed": "~1x"},
            "large-v3": {"size_mb": 2900, "params": "1550M", "speed": "~1x"},
        }

        info = model_sizes.get(self.model_name, {})

        return {
            "name": self.model_name,
            "size_mb": info.get("size_mb", "unknown"),
            "parameters": info.get("params", "unknown"),
            "relative_speed": info.get("speed", "unknown"),
            "device": self.device,
            "loaded": self.model is not None
        }

    def set_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """
        Set callback for progress updates

        Args:
            callback: Function(message: str, progress: float) called during operations
        """
        self.on_progress = callback

    @staticmethod
    def list_available_models() -> list[str]:
        """
        Get list of available Whisper models

        Returns:
            List of model names
        """
        return [model.value for model in WhisperModel]

    @staticmethod
    def get_model_size(model_name: str) -> int:
        """
        Get model size in MB

        Args:
            model_name: Model name

        Returns:
            Size in MB
        """
        sizes = {
            "tiny": 75,
            "base": 142,
            "small": 466,
            "medium": 1500,
            "large-v2": 2900,
            "large-v3": 2900,
        }
        return sizes.get(model_name, 0)


def test_whisper_engine():
    """Test the Whisper engine"""
    import time

    print("Testing Whisper Engine")
    print("=" * 60)

    # Create engine with tiny model for faster testing
    print("\n1. Creating Whisper engine...")
    engine = WhisperEngine(model_name="tiny")

    # Set up progress callback
    def on_progress(message, progress):
        print(f"   Progress: {message} ({progress:.0%})")

    engine.set_progress_callback(on_progress)

    # Load model
    print("\n2. Loading model...")
    success = engine.load_model()
    print(f"   Model loaded: {success}")

    # Get model info
    print("\n3. Model info:")
    info = engine.get_model_info()
    for key, value in info.items():
        print(f"   {key}: {value}")

    # Test transcription with sample audio
    print("\n4. Testing transcription...")
    print("   Generating test audio (440Hz sine wave = 'A' note)...")

    # Generate 3 seconds of test audio
    sample_rate = 16000
    duration = 3.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)

    try:
        result = engine.transcribe(audio, language="en")
        print(f"\n   Transcription: '{result['text']}'")
        print(f"   Language: {result['language']}")
        print(f"   Duration: {result['duration']:.2f}s")
        print(f"   Segments: {len(result['segments'])}")
    except Exception as e:
        print(f"   Note: Transcription of sine wave failed (expected): {e}")

    # Test model switching
    print("\n5. Testing model switching...")
    print("   (Skipping for faster testing - would download another model)")

    print("\n✓ Whisper engine test complete!")
    print("\nAvailable models:")
    for model in WhisperEngine.list_available_models():
        size = WhisperEngine.get_model_size(model)
        print(f"  • {model}: {size}MB")


if __name__ == "__main__":
    test_whisper_engine()
