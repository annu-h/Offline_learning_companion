"""
Lumi - Text-to-Speech (TTS) Module
100% Offline speech synthesis using pyttsx3 and SAPI5.
Calibrated for child-friendly, clear, and engaging voice output.
"""

import threading
from typing import Optional, Callable
import pyttsx3
from Python.serial_comm import send_signal

_TTS_LOCK = threading.Lock()


def get_configured_engine(rate: int = 140, volume: float = 1.0) -> pyttsx3.Engine:
    """Initializes and configures pyttsx3 engine with child-friendly settings."""
    engine = pyttsx3.init()

    # Rate setting
    engine.setProperty("rate", rate)

    # Volume setting (clamped between 0.0 and 1.0 for SAPI5)
    safe_volume = max(0.0, min(1.0, float(volume)))
    engine.setProperty("volume", safe_volume)

    # Voice selection: Prefer friendly female voice (Zira, Hazel, Susan) if available
    try:
        voices = engine.getProperty("voices")
        if voices:
            selected_voice = voices[0].id
            # Search for preferred female voices
            for v in voices:
                v_name = (v.name or "").lower()
                if "zira" in v_name or "female" in v_name or "hazel" in v_name or "susan" in v_name:
                    selected_voice = v.id
                    break
            # Fallback to second voice if available and no specific match
            if selected_voice == voices[0].id and len(voices) > 1:
                selected_voice = voices[1].id
            engine.setProperty("voice", selected_voice)
    except Exception:
        pass

    return engine


def _safe_print_speech(text: str) -> None:
    """Safely prints speech text to console without throwing UnicodeEncodeError on Windows."""
    msg = f"[Lumi]: {text}"
    try:
        print(f"🔊 Lumi: {text}")
    except (UnicodeEncodeError, Exception):
        try:
            print(msg)
        except Exception:
            pass


def speak(
    text: str,
    rate: int = 140,
    volume: float = 1.0,
    on_start: Optional[Callable[[], None]] = None,
    on_finish: Optional[Callable[[], None]] = None
) -> None:
    """
    Speaks the given text offline.
    Signals hardware and updates status callbacks.
    """
    if not text or not str(text).strip():
        return

    clean_text = str(text).strip()
    _safe_print_speech(clean_text)

    with _TTS_LOCK:
        try:
            send_signal("S")  # Speaking LED signal
            if on_start:
                try:
                    on_start()
                except Exception:
                    pass

            engine = get_configured_engine(rate=rate, volume=volume)
            engine.say(clean_text)
            engine.runAndWait()
            try:
                engine.stop()
            except Exception:
                pass
        except Exception as e:
            print(f"⚠️ TTS Error: {e}")
        finally:
            send_signal("I")  # Idle LED signal
            if on_finish:
                try:
                    on_finish()
                except Exception:
                    pass


def speak_async(
    text: str,
    rate: int = 140,
    volume: float = 1.0,
    on_start: Optional[Callable[[], None]] = None,
    on_finish: Optional[Callable[[], None]] = None
) -> threading.Thread:
    """Runs speak in a separate daemon thread so it doesn't block callers."""
    thread = threading.Thread(
        target=speak,
        args=(text, rate, volume, on_start, on_finish),
        daemon=True
    )
    thread.start()
    return thread


if __name__ == "__main__":
    speak("Hello! I am Lumi, your friendly offline learning companion.")
