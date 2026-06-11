"""
Arduino status monitoring and response handling.
"""
import time
from typing import Any

import cv2

from arduino.seralizer import (
    parse_arduino_response,
    read_arduino_line,
    send_cancel,
    wait_for_arduino_response,
)


def wait_for_arduino_status(arduino: Any, timeout_seconds: int = 30) -> dict[str, Any]:
    """
    Wait for a status response from Arduino.

    Pressing ESC sends CANCEL to the firmware and waits for CANCELLED.

    Args:
        arduino: Arduino serial connection
        timeout_seconds: Timeout in seconds

    Returns:
        Parsed response dictionary with a ``status`` key

    Raises:
        TimeoutError: If no response received within timeout
    """
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            print("[Arduino] Emergency stop requested. Sending CANCEL.")
            send_cancel(arduino)
            try:
                return wait_for_arduino_response(arduino, timeout_seconds=5)
            except TimeoutError:
                print("[Arduino] Timed out waiting for CANCELLED after ESC.")
                return {"status": "cancelled", "raw": "CANCELLED"}

        line = read_arduino_line(arduino)
        if not line:
            continue

        parsed = parse_arduino_response(line)
        if parsed is None:
            continue

        if parsed["status"] == "ready":
            continue

        return parsed

    raise TimeoutError("Timed out waiting for Arduino status response.")
