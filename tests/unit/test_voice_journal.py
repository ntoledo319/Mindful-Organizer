"""Tests for VoiceJournal backend (src/wellness/voice_journal.py)."""

from __future__ import annotations

import wave
from unittest.mock import MagicMock

import numpy as np
import pytest

from wellness import voice_journal as vj_module
from wellness.voice_journal import VoiceJournal


class TestVoiceJournalUnavailable:
    def test_instantiation_with_temp_data_dir(self, tmp_path):
        data_dir = tmp_path / "voice_journal"
        journal = VoiceJournal(data_dir=data_dir)
        assert journal.data_dir == data_dir
        assert not journal.is_available
        assert "sounddevice is not installed" in journal.reason

    def test_is_available_false_when_sounddevice_missing(self):
        journal = VoiceJournal()
        assert journal.is_available is False

    def test_start_recording_raises_when_unavailable(self):
        journal = VoiceJournal()
        with pytest.raises(RuntimeError, match="Voice recording is not available"):
            journal.start_recording()

    def test_stop_recording_raises_when_unavailable(self):
        journal = VoiceJournal()
        with pytest.raises(RuntimeError, match="Voice recording is not available"):
            journal.stop_recording()

    def test_stop_recording_without_starting_raises(self, monkeypatch):
        monkeypatch.setattr(vj_module, "_HAS_SOUNDDEVICE", True)
        monkeypatch.setattr(vj_module, "sd", MagicMock(), raising=False)
        journal = VoiceJournal()
        journal.is_available = True
        with pytest.raises(RuntimeError, match="Recording was not started"):
            journal.stop_recording()


class TestVoiceJournalAvailable:
    @pytest.fixture
    def mock_sd(self, monkeypatch):
        sd_mock = MagicMock()
        monkeypatch.setattr(vj_module, "_HAS_SOUNDDEVICE", True)
        monkeypatch.setattr(vj_module, "sd", sd_mock, raising=False)
        return sd_mock

    @pytest.fixture
    def journal(self, mock_sd, tmp_path):
        j = VoiceJournal(data_dir=tmp_path)
        j.is_available = True
        return j

    def test_start_recording_initializes_stream(self, journal, mock_sd):
        mock_stream = MagicMock()
        mock_sd.InputStream.return_value = mock_stream

        journal.start_recording()

        mock_sd.InputStream.assert_called_once_with(
            samplerate=VoiceJournal.SAMPLE_RATE,
            channels=VoiceJournal.CHANNELS,
            dtype="int16",
            callback=journal._audio_callback,
        )
        mock_stream.start.assert_called_once()
        assert journal._stream is mock_stream

    def test_audio_callback_appends_frames(self, journal):
        mock_frame = MagicMock()
        mock_frame.copy.return_value = mock_frame

        journal._audio_callback(mock_frame, 1024, None, None)
        assert len(journal._frames) == 1
        assert journal._frames[0] is mock_frame

    def test_stop_recording_saves_wav(self, journal, mock_sd, tmp_path):
        mock_stream = MagicMock()
        mock_sd.InputStream.return_value = mock_stream

        journal.start_recording()

        frame = np.array([[100], [200], [300]], dtype=np.int16)
        journal._frames = [frame]

        path = journal.stop_recording()

        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()
        assert path.exists()
        assert path.suffix == ".wav"

        with wave.open(str(path), "rb") as wf:
            assert wf.getnchannels() == VoiceJournal.CHANNELS
            assert wf.getsampwidth() == 2
            assert wf.getframerate() == VoiceJournal.SAMPLE_RATE
            assert wf.getnframes() == 3

    def test_recording_without_starting_raises(self, journal):
        with pytest.raises(RuntimeError, match="Recording was not started"):
            journal.stop_recording()
