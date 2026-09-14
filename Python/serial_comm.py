"""
Lumi - ESP32 Serial Communication Module
Optional hardware interface for LED and buzzer status indicators.
100% Fail-safe: if no hardware is connected, silently and safely operates in software-only mode.
"""

import threading
from typing import Optional, Any

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


_SERIAL_LOCK = threading.Lock()
_SERIAL_PORT: Optional[Any] = None if not SERIAL_AVAILABLE else None
_IS_CONNECTED: bool = False


def find_esp32_port() -> Optional[str]:
    """Scans available serial ports for CP210x, CH340, FTDI, or USB Serial devices."""
    if not SERIAL_AVAILABLE:
        return None
    try:
        ports = serial.tools.list_ports.comports()
        for port in ports:
            desc = (port.description or "").lower()
            hwid = (port.hwid or "").lower()
            if any(k in desc or k in hwid for k in ["cp210", "ch340", "ftdi", "usb serial", "esp32", "arduino"]):
                return port.device
        if ports:
            return ports[0].device
    except Exception:
        pass
    return None


def init_serial(port: Optional[str] = None, baudrate: int = 115200) -> bool:
    """Attempts to connect to ESP32 on specified port or auto-detected port."""
    global _SERIAL_PORT, _IS_CONNECTED
    if not SERIAL_AVAILABLE:
        _IS_CONNECTED = False
        return False

    with _SERIAL_LOCK:
        if _IS_CONNECTED and _SERIAL_PORT and _SERIAL_PORT.is_open:
            return True

        target_port = port or find_esp32_port()
        if not target_port:
            _IS_CONNECTED = False
            return False

        try:
            _SERIAL_PORT = serial.Serial(target_port, baudrate=baudrate, timeout=0.5)
            _IS_CONNECTED = True
            print(f"🔌 Hardware connected: ESP32 on {target_port}")
            return True
        except Exception:
            _SERIAL_PORT = None
            _IS_CONNECTED = False
            return False


def is_connected() -> bool:
    """Returns whether hardware is actively connected."""
    global _IS_CONNECTED, _SERIAL_PORT
    with _SERIAL_LOCK:
        if not _IS_CONNECTED or _SERIAL_PORT is None:
            return False
        try:
            return _SERIAL_PORT.is_open
        except Exception:
            _IS_CONNECTED = False
            return False


def send_signal(cmd: str) -> bool:
    """
    Sends a 1-character or short status command to ESP32.
    Commands:
      'L' : Listening (Blue LED)
      'S' : Speaking (Green LED)
      'P' : Processing (Yellow/Amber LED)
      'C' : Correct Answer (Green Flash)
      'W' : Wrong / Try Again (Red Flash)
      'I' : Idle (Breathing / Dim LED)
    """
    global _SERIAL_PORT, _IS_CONNECTED
    if not SERIAL_AVAILABLE or not _IS_CONNECTED or _SERIAL_PORT is None:
        return False

    with _SERIAL_LOCK:
        try:
            if _SERIAL_PORT.is_open:
                msg = (cmd.strip() + "\n").encode("utf-8")
                _SERIAL_PORT.write(msg)
                _SERIAL_PORT.flush()
                return True
        except Exception:
            # Device disconnected
            try:
                if _SERIAL_PORT:
                    _SERIAL_PORT.close()
            except Exception:
                pass
            _SERIAL_PORT = None
            _IS_CONNECTED = False
    return False


def close_serial() -> None:
    """Closes serial connection safely."""
    global _SERIAL_PORT, _IS_CONNECTED
    with _SERIAL_LOCK:
        if _SERIAL_PORT:
            try:
                _SERIAL_PORT.close()
            except Exception:
                pass
            _SERIAL_PORT = None
        _IS_CONNECTED = False
