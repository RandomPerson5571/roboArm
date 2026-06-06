"""
Arduino status monitoring and response handling.
"""
import json
import time
from typing import Any

import cv2


def wait_for_arduino_status(arduino: Any, timeout_seconds: int = 30) -> dict[str, Any]:
    """
    Wait for a status response from Arduino.
    
    Args:
        arduino: Arduino connection object with readline() method
        timeout_seconds: Timeout in seconds
        
    Returns:
        Parsed JSON response dictionary
        
    Raises:
        TimeoutError: If no response received within timeout
    """
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            return {"status": "cancelled"}

        raw_data = arduino.readline()
        if not raw_data:
            continue

        line = raw_data.decode("utf-8", errors="ignore").strip()
        if not line:
            continue

        try:
            return json.loads(line)
        except json.JSONDecodeError:
            print(f"[Arduino] Ignoring malformed response: {line}")
            continue

    raise TimeoutError("Timed out waiting for Arduino status response.")
