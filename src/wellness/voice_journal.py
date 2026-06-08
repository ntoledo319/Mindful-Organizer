"""Voice journaling with graceful degradation.

Tries to use ``sounddevice`` for actual recording. If unavailable,
clearly reports that voice journaling is coming soon and refuses to
generate silent/deceptive audio.
"""

from __future__ import annotations

import logging
import wave
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:
    import sounddevice as sd
    import numpy as np

    _HAS_SOUNDDEVICE = True
except ImportError:
    _HAS_SOUNDDEVICE = False


class VoiceJournal:
    """Voice journal recorder with graceful degradation.

    When ``sounddevice`` is available, the recorder can start/stop
    capture and save to WAV.  When it is not available, every
    recording method raises ``RuntimeError`` with a clear message so
    the UI can show a warm "coming soon" screen instead of producing
    silent or empty audio files.
    """

    SAMPLE_RATE = 44100
    CHANNELS = 1

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir
        self.is_available = _HAS_SOUNDDEVICE
        self.reason = "" if _HAS_SOUNDDEVICE else "sounddevice is not installed"
        self._stream: Any = None
        self._frames: list[Any] = []

    # -- public API --------------------------------------------------------

    def start_recording(self) -> None:
        """Begin recording audio from the default input device."""
        if not self.is_available:
            raise RuntimeError("Voice recording is not available. " + self.reason)
        self._frames = []
        try:
            self._stream = sd.InputStream(
                samplerate=self.SAMPLE_RATE,
                channels=self.CHANNELS,
                dtype="int16",
                callback=self._audio_callback,
            )
            self._stream.start()
            logger.info("Voice recording started")
        except Exception as exc:
            logger.exception("Failed to start voice recording")
            raise RuntimeError(f"Could not start recording: {exc}") from exc

    def stop_recording(self) -> Path:
        """Stop recording and save the captured audio to a WAV file.

        Returns:
            Path to the saved WAV file.
        """
        if not self.is_available:
            raise RuntimeError("Voice recording is not available. " + self.reason)
        if self._stream is None:
            raise RuntimeError("Recording was not started.")
        try:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        except Exception as exc:
            logger.exception("Error stopping voice stream")
            raise RuntimeError(f"Could not stop recording: {exc}") from exc

        path = self._save_wav()
        logger.info("Voice recording saved to %s", path)
        return path

    def get_status(self) -> dict[str, Any]:
        """Return a dict describing availability and any blocker."""
        return {
            "available": self.is_available,
            "reason": self.reason,
            "recording": self._stream is not None,
        }

    # -- internals ---------------------------------------------------------

    def _audio_callback(self, indata: Any, _frames: int, _time: Any, status: Any) -> None:
        if status:
            logger.debug("Audio callback status: %s", status)
        self._frames.append(indata.copy())

    def _save_wav(self) -> Path:
        if self.data_dir is None:
            from core.paths import get_data_dir

            self.data_dir = get_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        path = self.data_dir / "voice_journal.wav"

        if not self._frames:
            raise RuntimeError("No audio frames captured.")

        audio = np.concatenate(self._frames, axis=0)
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(audio.tobytes())
        return path
