"""
Whisper Model Manager

Handles downloading, caching, and managing Whisper models.
"""

import os
from pathlib import Path
from typing import Optional, Callable, Dict
import whisper
from whisper import _MODELS


class ModelManager:
    """
    Manages Whisper model downloads and caching

    Provides progress tracking and model information.
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize model manager

        Args:
            cache_dir: Directory to cache models (default: ~/.cache/whisper)
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".cache" / "whisper"

        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Progress callback
        self.on_progress: Optional[Callable[[str, str, float], None]] = None

    def is_model_downloaded(self, model_name: str) -> bool:
        """
        Check if a model is already downloaded

        Args:
            model_name: Model name (tiny, base, small, medium, large-v2, large-v3)

        Returns:
            True if model exists in cache
        """
        if model_name not in _MODELS:
            return False

        # Get model URL and expected filename
        url = _MODELS[model_name]
        filename = os.path.basename(url)
        model_path = self.cache_dir / filename

        return model_path.exists()

    def get_model_path(self, model_name: str) -> Optional[Path]:
        """
        Get path to cached model file

        Args:
            model_name: Model name

        Returns:
            Path to model file, or None if not downloaded
        """
        if not self.is_model_downloaded(model_name):
            return None

        url = _MODELS[model_name]
        filename = os.path.basename(url)
        return self.cache_dir / filename

    def download_model(self, model_name: str) -> bool:
        """
        Download a Whisper model

        Args:
            model_name: Model name to download

        Returns:
            True if download successful
        """
        if model_name not in _MODELS:
            print(f"✗ Unknown model: {model_name}")
            return False

        if self.is_model_downloaded(model_name):
            print(f"✓ Model '{model_name}' already downloaded")
            return True

        try:
            print(f"Downloading Whisper model '{model_name}'...")

            if self.on_progress:
                self.on_progress(model_name, "Starting download...", 0.0)

            # Load model (this triggers download)
            # Whisper handles the downloading internally
            model = whisper.load_model(model_name, download_root=str(self.cache_dir))

            if self.on_progress:
                self.on_progress(model_name, "Download complete", 1.0)

            print(f"✓ Model '{model_name}' downloaded successfully")

            # Clean up model from memory
            del model

            return True

        except Exception as e:
            print(f"✗ Error downloading model: {e}")
            if self.on_progress:
                self.on_progress(model_name, f"Error: {e}", 0.0)
            return False

    def delete_model(self, model_name: str) -> bool:
        """
        Delete a cached model

        Args:
            model_name: Model name to delete

        Returns:
            True if deletion successful
        """
        model_path = self.get_model_path(model_name)

        if not model_path:
            print(f"Model '{model_name}' not found")
            return False

        try:
            model_path.unlink()
            print(f"✓ Deleted model '{model_name}'")
            return True
        except Exception as e:
            print(f"✗ Error deleting model: {e}")
            return False

    def get_all_models(self) -> Dict[str, Dict]:
        """
        Get information about all available models

        Returns:
            Dictionary mapping model names to their info
        """
        models = {}

        for model_name in _MODELS.keys():
            models[model_name] = self.get_model_info(model_name)

        return models

    def get_model_info(self, model_name: str) -> Dict:
        """
        Get information about a specific model

        Args:
            model_name: Model name

        Returns:
            Dictionary with model information
        """
        sizes = {
            "tiny": {"size_mb": 75, "params": "39M", "relative_speed": "~10x"},
            "base": {"size_mb": 142, "params": "74M", "relative_speed": "~7x"},
            "small": {"size_mb": 466, "params": "244M", "relative_speed": "~4x"},
            "medium": {"size_mb": 1500, "params": "769M", "relative_speed": "~2x"},
            "large-v2": {"size_mb": 2900, "params": "1550M", "relative_speed": "~1x"},
            "large-v3": {"size_mb": 2900, "params": "1550M", "relative_speed": "~1x"},
        }

        info = sizes.get(model_name, {
            "size_mb": "unknown",
            "params": "unknown",
            "relative_speed": "unknown"
        })

        return {
            "name": model_name,
            "downloaded": self.is_model_downloaded(model_name),
            "size_mb": info["size_mb"],
            "parameters": info["params"],
            "relative_speed": info["relative_speed"],
            "path": str(self.get_model_path(model_name)) if self.is_model_downloaded(model_name) else None
        }

    def get_cache_size(self) -> int:
        """
        Get total size of cached models in MB

        Returns:
            Total cache size in MB
        """
        total_size = 0

        for file in self.cache_dir.glob("*.pt"):
            total_size += file.stat().st_size

        return total_size // (1024 * 1024)  # Convert to MB

    def set_progress_callback(self, callback: Callable[[str, str, float], None]) -> None:
        """
        Set callback for progress updates

        Args:
            callback: Function(model_name: str, message: str, progress: float)
        """
        self.on_progress = callback

    def get_recommended_model(self, priority: str = "balanced") -> str:
        """
        Get recommended model based on priority

        Args:
            priority: "speed", "balanced", or "accuracy"

        Returns:
            Recommended model name
        """
        recommendations = {
            "speed": "tiny",
            "balanced": "medium",
            "accuracy": "large-v3"
        }

        return recommendations.get(priority, "medium")


def test_model_manager():
    """Test the model manager"""
    print("Testing Model Manager")
    print("=" * 60)

    # Create manager
    manager = ModelManager()

    # Set up progress callback
    def on_progress(model_name, message, progress):
        print(f"   [{model_name}] {message} ({progress:.0%})")

    manager.set_progress_callback(on_progress)

    # Get all models info
    print("\n1. Available models:")
    models = manager.get_all_models()
    for name, info in models.items():
        status = "✓ Downloaded" if info["downloaded"] else "○ Not downloaded"
        print(f"   {status} {name}: {info['size_mb']}MB, {info['parameters']} params, {info['relative_speed']} speed")

    # Check cache size
    print(f"\n2. Cache size: {manager.get_cache_size()}MB")
    print(f"   Cache directory: {manager.cache_dir}")

    # Check if specific model is downloaded
    print("\n3. Checking specific models:")
    for model in ["tiny", "medium", "large-v3"]:
        downloaded = manager.is_model_downloaded(model)
        status = "✓" if downloaded else "✗"
        print(f"   {status} {model}: {'Downloaded' if downloaded else 'Not downloaded'}")

    # Get recommendations
    print("\n4. Recommended models:")
    for priority in ["speed", "balanced", "accuracy"]:
        rec = manager.get_recommended_model(priority)
        print(f"   {priority.capitalize()}: {rec}")

    print("\n✓ Model manager test complete!")


if __name__ == "__main__":
    test_model_manager()
