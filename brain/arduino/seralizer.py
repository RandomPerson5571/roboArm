import json
import time
import serial

from typing import Any

from config import TOOL_CONFIG

CANCEL_COMMAND = "CANCEL"
ARDUINO_READY = "Ready"
ARDUINO_SUCCESS = "SUCCESS"
ARDUINO_ERROR = "ERROR"
ARDUINO_CANCELLED = "CANCELLED"

_STATUS_MAP = {
    ARDUINO_SUCCESS: "success",
    ARDUINO_ERROR: "error",
    ARDUINO_CANCELLED: "cancelled",
    ARDUINO_READY: "ready",
}


def parse_classifier_response(raw_response: Any) -> dict[str, Any]:
    if isinstance(raw_response, dict):
        return raw_response

    if isinstance(raw_response, str):
        payload = raw_response.strip()

        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            for opener, closer in (("[", "]"), ("{", "}")):
                start = payload.find(opener)
                end = payload.rfind(closer)
                if start != -1 and end != -1 and start < end:
                    candidate = payload[start:end + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        continue

    raise ValueError("Could not parse classifier response as JSON.")


def parse_arduino_response(line: str) -> dict[str, Any] | None:
    """Map a single Arduino serial line to a status dictionary."""
    text = line.strip()
    if not text:
        return None

    status = _STATUS_MAP.get(text)
    if status is None:
        print(f"[Arduino] Ignoring unrecognized response: {text}")
        return None

    return {"status": status, "raw": text}


def read_arduino_line(arduino: serial.Serial) -> str | None:
    raw = arduino.readline()
    if not raw:
        return None

    line = raw.decode("utf-8", errors="ignore").strip()
    return line or None


def wait_for_arduino_response(
    arduino: serial.Serial,
    *,
    timeout_seconds: float = 30,
    ignore_ready: bool = True,
) -> dict[str, Any]:
    """Wait for a recognized Arduino response line."""
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        line = read_arduino_line(arduino)
        if line is None:
            continue

        parsed = parse_arduino_response(line)
        if parsed is None:
            continue

        if ignore_ready and parsed["status"] == "ready":
            continue

        return parsed

    raise TimeoutError("Timed out waiting for Arduino response.")


def get_arduino(
    port: str = TOOL_CONFIG.get("SERIAL_PORT", "COM3"),
    baudrate: int = TOOL_CONFIG.get("SERIAL_BAUDRATE", 115200),
) -> serial.Serial:
    arduino = serial.Serial(port=port, baudrate=baudrate, timeout=0.1)
    time.sleep(2)
    arduino.reset_input_buffer()

    response = wait_for_arduino_response(
        arduino,
        timeout_seconds=10,
        ignore_ready=False,
    )
    if response.get("status") != "ready":
        raise RuntimeError(f"Expected '{ARDUINO_READY}' on connect, got: {response.get('raw')}")

    print("[Arduino] Connected and ready.")
    return arduino


def send_data(arduino: serial.Serial, data: str) -> None:
    arduino.write(data.encode("utf-8"))
    print(f"Sent: {data.rstrip()}")


def send_servo_angles(arduino: serial.Serial, angles_line: str) -> None:
    """Send a comma-separated servo angle command."""
    send_data(arduino, f"{angles_line}\n")


def send_cancel(arduino: serial.Serial) -> None:
    """Send the firmware cancel command."""
    send_data(arduino, f"{CANCEL_COMMAND}\n")
