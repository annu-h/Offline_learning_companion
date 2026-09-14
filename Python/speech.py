"""
Lumi - Speech Recognition Module
100% Offline voice input using local faster-whisper (CPU int8) and webrtcvad.
Loads models strictly from Models/whisper-base-en without any internet connection.
Features responsive streaming chunk capture with dynamic silence detection.
"""

import sys
import time
import threading
from pathlib import Path
from typing import Optional, Callable

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import numpy as np
import sounddevice as sd
import webrtcvad
from faster_whisper import WhisperModel

from Python.serial_comm import send_signal

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "Models" / "whisper-base-en"

SAMPLE_RATE = 16000
FRAME_DURATION_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)  # 480 samples

_MODEL_LOCK = threading.Lock()
_WHISPER_MODEL: Optional[WhisperModel] = None


def get_whisper_model() -> WhisperModel:
    """Loads and caches the local offline Whisper model."""
    global _WHISPER_MODEL
    with _MODEL_LOCK:
        if _WHISPER_MODEL is None:
            if not MODEL_PATH.exists():
                raise FileNotFoundError(
                    f"Local Whisper model not found at {MODEL_PATH}. Ensure Models/whisper-base-en exists."
                )
            print("⏳ Loading local offline Whisper model...")
            _WHISPER_MODEL = WhisperModel(
                str(MODEL_PATH),
                device="cpu",
                compute_type="int8",
                cpu_threads=4
            )
            print("✅ Local Whisper model loaded.")
        return _WHISPER_MODEL


def listen(
    status_callback: Optional[Callable[[str], None]] = None,
    max_seconds: float = 8.0,
    silence_seconds: float = 1.8
) -> str:
    """
    Listens for child speech using streaming VAD and transcribes using local Whisper.
    Returns transcribed text (or empty string if no speech or error).
    """
    vad = webrtcvad.Vad(2)  # Mode 2: balanced aggressiveness

    print("\n🎤 Listening... Speak naturally!")
    send_signal("L")  # Listening signal

    if status_callback:
        try:
            status_callback("listening")
        except Exception:
            pass

    recorded_frames = []
    speech_started = False
    silence_frames = 0
    max_silence_frames = int(silence_seconds * 1000 / FRAME_DURATION_MS)
    max_total_frames = int(max_seconds * 1000 / FRAME_DURATION_MS)

    try:
        # Open continuous audio input stream
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=FRAME_SIZE
        ) as stream:
            for _ in range(max_total_frames):
                frame, overflowed = stream.read(FRAME_SIZE)
                frame_data = np.squeeze(frame)
                raw_bytes = frame_data.tobytes()

                # VAD detection
                try:
                    is_speech = vad.is_speech(raw_bytes, SAMPLE_RATE)
                except Exception:
                    # Fallback amplitude threshold
                    amplitude = np.max(np.abs(frame_data))
                    is_speech = amplitude > 1200

                if is_speech:
                    if not speech_started:
                        speech_started = True
                        if status_callback:
                            try:
                                status_callback("speech_detected")
                            except Exception:
                                pass
                    silence_frames = 0
                    recorded_frames.append(frame_data)
                else:
                    if speech_started:
                        recorded_frames.append(frame_data)
                        silence_frames += 1
                        if silence_frames >= max_silence_frames:
                            print("🛑 Speech finished.")
                            break

    except Exception as e:
        print(f"⚠️ Microphone / PortAudio warning: {e}")
        send_signal("I")
        if status_callback:
            try:
                status_callback("idle")
            except Exception:
                pass
        return ""

    if not speech_started or not recorded_frames:
        print("❌ No speech detected.")
        send_signal("I")
        if status_callback:
            try:
                status_callback("idle")
            except Exception:
                pass
        return ""

    # Process audio
    send_signal("P")  # Processing signal
    if status_callback:
        try:
            status_callback("processing")
        except Exception:
            pass

    try:
        audio_concat = np.concatenate(recorded_frames)
        audio_float = audio_concat.astype(np.float32) / 32768.0

        model = get_whisper_model()
        segments, info = model.transcribe(
            audio_float,
            language="en",
            vad_filter=True,
            beam_size=1
        )

        text = "".join(segment.text for segment in segments).strip()

        if text:
            print(f"📝 You said: {text}\n")
        else:
            print("❌ Speech could not be recognized.\n")

        return text

    except Exception as e:
        print(f"⚠️ Whisper transcription error: {e}")
        return ""
    finally:
        send_signal("I")
        if status_callback:
            try:
                status_callback("idle")
            except Exception:
                pass


if __name__ == "__main__":
    from Python.tts import speak
    print("Testing speech module...")
    user_text = listen()
    if user_text:
        speak(f"I heard you say {user_text}")
    else:
        speak("I did not hear anything.")
