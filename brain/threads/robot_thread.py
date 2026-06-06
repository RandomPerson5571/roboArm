"""
Robot state machine thread worker.
"""
import threading
import queue
from typing import Any

from speech.text_to_speech import announce_status
from .message_types import IntentData


def robot_state_machine_thread_worker(
    queue_in: queue.Queue,
    stop_event: threading.Event,
    arduino: Any = None,
) -> None:
    """
    Thread 5: Execute robot state machine - process task plans and send to Arduino.
    Consumes IntentData from queue_in.
    """
    # Import here to avoid circular dependencies
    from intent.task_builder import build_task_plan
    from arduino.executor import process_task_queue

    try:
        while not stop_event.is_set():
            try:
                intent_data = queue_in.get(timeout=0.5)
            except queue.Empty:
                continue

            print(f"[Robot] Received {len(intent_data.commands)} command(s).")

            try:
                task_queue = [
                    build_task_plan(command, intent_data.detections, intent_data.frame_shape)
                    for command in intent_data.commands
                ]

                print(f"[Robot] Built task queue with {len(task_queue)} task(s).")

                if arduino:
                    stop_requested = process_task_queue(arduino, task_queue)
                    if stop_requested:
                        stop_event.set()
                else:
                    print("[Robot] Skipping execution (no Arduino connected).")
                    print(f"[Robot] Would execute: {task_queue}")

            except Exception as e:
                print(f"[Robot] Command processing failed: {e}")
                announce_status(f"Robot command failed: {e}")

    except Exception as e:
        print(f"[Robot] Error: {e}")
        stop_event.set()
