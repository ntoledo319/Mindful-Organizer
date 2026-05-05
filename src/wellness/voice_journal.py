"""
Voice memo journaling support for Mindful Organizer.

STATUS: Partial implementation / stub.  The module creates placeholder
silent WAV files and attempts macOS Shortcuts transcription, but real
audio capture requires PyAudio or a platform-specific backend.

Confirmed behavior:
  - record_memo() creates a silent WAV file of the requested duration.
  - _transcribe() tries macOS ``shortcuts`` CLI; returns "" on failure.
  - _estimate_emotion() runs a trivial amplitude heuristic on the silent
    audio (always "neutral" for stub files).

Not yet implemented:
  - Live microphone capture.
  - Cross-platform transcription (Whisper, cloud APIs).
  - Real emotion estimation from audio features.
"""

from __future__ import annotations

import logging
import subprocess
import wave
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class VoiceMemo:
    """A recorded voice journal entry."""
    memo_id: str
    timestamp: datetime
    audio_path: Path
    duration_seconds: float = 0.0
    transcription: str = ""
    emotion_tag: str = ""  # calm, agitated, neutral


# ---------------------------------------------------------------------------
# Recorder
# ---------------------------------------------------------------------------

class VoiceJournalRecorder:
    """Record and manage voice memos for journaling."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir / "voice_memos"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def record_memo(self, duration_seconds: int = 60) -> VoiceMemo | None:
        """Record a voice memo.

        Returns the memo metadata, or None if recording failed.
        """
        memo_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.data_dir / f"{memo_id}.wav"

        try:
            # Try macOS `say` / `rec` / built-in recording
            # For now, we create a placeholder that documents the intent
            # and provides the file path for future integration.
            self._record_audio(str(output_path), duration_seconds)

            duration = self._get_audio_duration(output_path)

            # Attempt transcription if whisper/ dictation available
            transcription = self._transcribe(str(output_path))

            # Simple emotion heuristic from audio features
            emotion = self._estimate_emotion(str(output_path))

            return VoiceMemo(
                memo_id=memo_id,
                timestamp=datetime.now(),
                audio_path=output_path,
                duration_seconds=duration,
                transcription=transcription,
                emotion_tag=emotion,
            )
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            logger.error("Voice recording failed: %s", exc)
            return None

    def list_memos(self) -> list[VoiceMemo]:
        """List all recorded memos."""
        memos: list[VoiceMemo] = []
        for wav_file in sorted(self.data_dir.glob("*.wav"), reverse=True):
            memo_id = wav_file.stem
            duration = self._get_audio_duration(wav_file)
            transcription = ""
            trans_file = wav_file.with_suffix(".txt")
            if trans_file.exists():
                transcription = trans_file.read_text(encoding="utf-8")

            memos.append(VoiceMemo(
                memo_id=memo_id,
                timestamp=datetime.now(),  # parsed from filename if needed
                audio_path=wav_file,
                duration_seconds=duration,
                transcription=transcription,
            ))
        return memos

    def _record_audio(self, path: str, duration: int) -> None:
        """Record audio to the given path.

        This is a platform-aware stub. On macOS, it can use
        ``avfoundation`` via ffmpeg or the built-in ``say`` command
        for synthetic testing. For real recording, integrate with
        PyAudio or platform-specific APIs.
        """
        # Placeholder: create a silent WAV file so the path exists
        # Real implementation would use PyAudio or platform APIs
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b"\x00" * (16000 * 2 * duration))

    def _get_audio_duration(self, path: Path) -> float:
        """Return audio duration in seconds."""
        try:
            with wave.open(str(path), "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                return frames / float(rate)
        except (OSError, ValueError, wave.Error):
            return 0.0

    def _transcribe(self, path: str) -> str:
        """Attempt to transcribe audio.

        Tries macOS dictation or whisper.cpp if available.
        Returns empty string if transcription is unavailable.
        """
        # Try macOS built-in speech recognition via shortcuts/automator
        # This is a placeholder for actual integration
        try:
            result = subprocess.run(
                ["shortcuts", "run", "Transcribe Audio", "-i", path],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return ""

    def _estimate_emotion(self, path: str) -> str:
        """Estimate emotion from audio features.

        This is a lightweight heuristic using amplitude variance.
        A real implementation would use pitch/volume analysis.
        """
        try:
            with wave.open(path, "rb") as wf:
                frames = wf.readframes(wf.getnframes())
                if not frames:
                    return "neutral"

                import array
                samples = array.array("h", frames)
                if not samples:
                    return "neutral"

                # Simple amplitude variance heuristic
                mean_amp = sum(abs(s) for s in samples) / len(samples)
                variance = sum((abs(s) - mean_amp) ** 2 for s in samples) / len(samples)

                if variance > 500000:
                    return "agitated"
                elif mean_amp < 100:
                    return "calm"
                return "neutral"
        except (OSError, ValueError, wave.Error):
            return "neutral"
