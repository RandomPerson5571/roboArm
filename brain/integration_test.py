"""
Command-processing thread worker.
"""
import queue
import threading
import time
from typing import Any

from arduino.seralizer import parse_classifier_response
from intent.intent_classifier import classify_intent
from intent.task_builder import build_task_plan
from speech.text_to_speech import announce_status
from speech.voice import capture_speech
from threads.message_types import IntentData, LatestFrameState
from arduino.seralizer import get_arduino



print("[Command] Capturing speech...")
voice_prompt = "pick up the cup"
if not voice_prompt:
    print("[Command] No speech captured.")

available_objects = ["cup"]
detections = [
    {
        "name": "cup",
        "bbox": (200.0, 150.0, 280.0, 230.0),
        "center_x": 240.0,
        "center_y": 190.0,
    }
]

print(f"[Command] Processing: {voice_prompt}")

try:
    classifier_response = classify_intent(
        voice_prompt,
        available_objects,
    )
    classifier_payload = parse_classifier_response(classifier_response)
    commands = classifier_payload.get("commands", [])

    intent_data = IntentData(
        classifier_response=classifier_response,
        commands=commands,
        detections=detections,
        frame_shape=(480, 640, 3),
        timestamp=time.time(),
    )
    print(f"[Command] Generated {len(commands)} command(s).")
except Exception as e:
    print(f"[Command] Failed to parse intent: {e}")

try:
    task_queue = [
        build_task_plan(command, intent_data.detections, intent_data.frame_shape)
        for command in intent_data.commands
    ]

    print(f"[Command] Built task queue with {len(task_queue)} task(s).")

    arduino = get_arduino()

    if arduino:
        from arduino.executor import process_task_queue

        stop_requested = process_task_queue(arduino, task_queue)

    else:
        print("[Command] Skipping execution (no Arduino connected).")
        print(f"[Command] Would execute: {task_queue}")

except Exception as e:
    print(f"[Command] Command processing failed: {e}")
