import json
import time
import serial

from typing import Any

from intent.step_types import TaskPlan

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

def get_arduino(port='COM3'):
    arduino = serial.Serial(port=port, baudrate=115200, timeout=0.1)
    time.sleep(2)

    return arduino

def send_json_data(arduino, data: TaskPlan):
    # send a plan containing a single task so Arduino receives plan/task/step format
    payload = {"plan": [data]}
    json_string = json.dumps(payload) + "\n"

    arduino.write(json_string.encode('utf-8'))
    print(f"Sent: {json_string}")

def wait_for_arduino(arduino) -> dict[str, any]:
    response_line = arduino.readline()
    if not response_line:
        return {}

    response_text = response_line.decode('utf-8', errors='ignore').strip()
    if not response_text:
        return {}

    return json.loads(response_text)

    return json_payload