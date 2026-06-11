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
from .message_types import IntentData, LatestFrameState


def command_thread_worker(
    control_queue: queue.Queue,
    latest_frame_state: LatestFrameState,
    stop_event: threading.Event,
    arduino: Any = None,
) -> None:
    """
    Process voice commands serially: capture speech, classify intent, and execute tasks.
    """
    try:
        while not stop_event.is_set():
            try:
                signal = control_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if signal != "CAPTURE":
                continue

            print("[Command] Capturing speech...")
            voice_prompt = capture_speech()
            if not voice_prompt:
                print("[Command] No speech captured.")
                continue

            latest_frame_data = latest_frame_state.get()
            if latest_frame_data is None:
                print("[Command] Warning: No frame data available yet.")
                announce_status("No camera frame is available yet. Please try again.")
                continue

            print(f"[Command] Processing: {voice_prompt}")

            try:
                classifier_response = classify_intent(
                    voice_prompt,
                    latest_frame_data.available_objects,
                )
                classifier_payload = parse_classifier_response(classifier_response)
                commands = classifier_payload.get("commands", [])

                intent_data = IntentData(
                    classifier_response=classifier_response,
                    commands=commands,
                    detections=latest_frame_data.detections,
                    frame_shape=latest_frame_data.frame.shape,
                    timestamp=time.time(),
                )
                print(f"[Command] Generated {len(commands)} command(s).")
            except Exception as e:
                print(f"[Command] Failed to parse intent: {e}")
                announce_status(f"Intent parsing failed: {e}")
                continue

            try:
                task_queue = [
                    build_task_plan(command, intent_data.detections, intent_data.frame_shape)
                    for command in intent_data.commands
                ]

                print(f"[Command] Built task queue with {len(task_queue)} task(s).")

                if arduino:
                    from arduino.executor import process_task_queue

                    stop_requested = process_task_queue(arduino, task_queue)
                    if stop_requested:
                        stop_event.set()
                else:
                    print("[Command] Skipping execution (no Arduino connected).")
                    print(f"[Command] Would execute: {task_queue}")

            except Exception as e:
                print(f"[Command] Command processing failed: {e}")
                announce_status(f"Robot command failed: {e}")

    except Exception as e:
        print(f"[Command] Error: {e}")
        stop_event.set()
