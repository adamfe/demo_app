"""
Audio Recorder for Voice Mode

Handles real-time audio recording from microphone with no warm-up delay.
"""

import numpy as np
import sounddevice as sd
from typing import Optional, Callable, List
import threading
import queue
from datetime import datetime


class AudioRecorder:
    """
    Real-time audio recorder with instant start

    Features:
    - No warm-up delay
    - Real-time audio level monitoring
    - Configurable sample rate and channels
    - Callback support for audio data
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        dtype: str = 'float32',
        blocksize: int = 1024,
        device: Optional[int] = None
    ):
        """
        Initialize audio recorder

        Args:
            sample_rate: Audio sample rate (Whisper uses 16kHz)
            channels: Number of audio channels (1 = mono)
            dtype: Audio data type
            blocksize: Buffer size for audio chunks
            device: Input device ID (None = default)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.blocksize = blocksize
        self.device = device

        # Recording state
        self.is_recording = False
        self.audio_data: List[np.ndarray] = []
        self.audio_queue = queue.Queue()

        # Stream
        self.stream: Optional[sd.InputStream] = None

        # Callbacks
        self.on_audio_chunk: Optional[Callable[[np.ndarray, float], None]] = None

        # Stats
        self.recording_start_time: Optional[datetime] = None
        self.current_level = 0.0

    def _audio_callback(self, indata, frames, time_info, status):
        """
        Callback called by sounddevice for each audio chunk

        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Timing information
            status: Stream status
        """
        if status:
            print(f"Audio callback status: {status}")

        if self.is_recording:
            # Copy data to prevent modifications
            audio_chunk = indata.copy()

            # Store in list
            self.audio_data.append(audio_chunk)

            # Calculate audio level (RMS)
            level = float(np.sqrt(np.mean(audio_chunk**2)))
            self.current_level = level

            # Call user callback if set
            if self.on_audio_chunk:
                try:
                    self.on_audio_chunk(audio_chunk, level)
                except Exception as e:
                    print(f"Error in audio chunk callback: {e}")

    def start_recording(self) -> bool:
        """
        Start recording audio

        Returns:
            True if recording started successfully
        """
        if self.is_recording:
            print("Already recording")
            return False

        try:
            # Clear previous recording
            self.audio_data = []
            self.recording_start_time = datetime.now()
            self.is_recording = True

            # Create and start stream
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                blocksize=self.blocksize,
                device=self.device,
                callback=self._audio_callback
            )
            self.stream.start()

            print(f"✓ Recording started (device: {self.device or 'default'})")
            return True

        except Exception as e:
            print(f"Error starting recording: {e}")
            self.is_recording = False
            return False

    def stop_recording(self) -> Optional[np.ndarray]:
        """
        Stop recording and return audio data

        Returns:
            Recorded audio as numpy array, or None if no data
        """
        if not self.is_recording:
            print("Not recording")
            return None

        try:
            self.is_recording = False

            # Stop stream
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

            # Combine all audio chunks
            if not self.audio_data:
                print("No audio data recorded")
                return None

            audio = np.concatenate(self.audio_data, axis=0)

            # Calculate duration
            duration = len(audio) / self.sample_rate
            print(f"✓ Recording stopped ({duration:.2f}s, {len(self.audio_data)} chunks)")

            return audio

        except Exception as e:
            print(f"Error stopping recording: {e}")
            return None

    def get_duration(self) -> float:
        """
        Get current recording duration in seconds

        Returns:
            Duration in seconds
        """
        if not self.is_recording or not self.recording_start_time:
            return 0.0

        elapsed = (datetime.now() - self.recording_start_time).total_seconds()
        return elapsed

    def get_current_level(self) -> float:
        """
        Get current audio level (RMS)

        Returns:
            Audio level between 0.0 and 1.0
        """
        return self.current_level

    def set_audio_chunk_callback(self, callback: Callable[[np.ndarray, float], None]) -> None:
        """
        Set callback for audio chunks (for real-time visualization)

        Args:
            callback: Function(audio_chunk, level) called for each audio chunk
        """
        self.on_audio_chunk = callback

    @staticmethod
    def list_input_devices() -> List[dict]:
        """
        List available audio input devices

        Returns:
            List of device dictionaries with 'id', 'name', 'channels'
        """
        devices = []
        for i, device in enumerate(sd.query_devices()):
            if device['max_input_channels'] > 0:
                devices.append({
                    'id': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
        return devices

    @staticmethod
    def get_default_input_device() -> Optional[dict]:
        """
        Get default input device

        Returns:
            Device dictionary or None
        """
        try:
            device_id = sd.default.device[0]  # Input device
            device = sd.query_devices(device_id)
            return {
                'id': device_id,
                'name': device['name'],
                'channels': device['max_input_channels'],
                'sample_rate': device['default_samplerate']
            }
        except Exception as e:
            print(f"Error getting default device: {e}")
            return None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.is_recording:
            self.stop_recording()


def test_audio_recorder():
    """Test the audio recorder"""
    import time

    print("Testing Audio Recorder")
    print("=" * 50)

    # List devices
    print("\nAvailable input devices:")
    devices = AudioRecorder.list_input_devices()
    for device in devices:
        print(f"  [{device['id']}] {device['name']} ({device['channels']} channels)")

    default = AudioRecorder.get_default_input_device()
    if default:
        print(f"\nDefault device: [{default['id']}] {default['name']}")

    # Test recording
    print("\nStarting 3-second test recording...")
    recorder = AudioRecorder()

    # Set up level callback
    def on_chunk(chunk, level):
        # Visualize level
        bars = int(level * 50)
        print(f"\rLevel: {'▓' * bars}{'░' * (50 - bars)} {level:.3f}", end='')

    recorder.set_audio_chunk_callback(on_chunk)

    # Record
    recorder.start_recording()
    time.sleep(3)
    audio = recorder.stop_recording()

    if audio is not None:
        print(f"\n✓ Recorded {len(audio)} samples ({len(audio)/16000:.2f}s)")
        print(f"  Shape: {audio.shape}")
        print(f"  Data type: {audio.dtype}")
        print(f"  Min: {audio.min():.3f}, Max: {audio.max():.3f}")
    else:
        print("\n✗ Recording failed")


if __name__ == "__main__":
    test_audio_recorder()
