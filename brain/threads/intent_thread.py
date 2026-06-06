"""
Intent parsing thread worker (Ollama-based).
"""
import time
import threading
import queue

from intent.intent_classifier import classify_intent
from arduino.seralizer import parse_classifier_response
from speech.text_to_speech import announce_status
from .message_types import FrameData, AudioData, IntentData


def intent_parser_thread_worker(
    queue_frame_in: queue.Queue,
    queue_audio_in: queue.Queue,
    queue_out: queue.Queue,
    stop_event: threading.Event,
) -> None:
    """
    Thread 4: Parse intent from transcribed text using Ollama.
    Consumes AudioData and FrameData, produces IntentData.
    """
    try:
        latest_frame_data: FrameData | None = None

        while not stop_event.is_set():
            # Get latest frame data (non-blocking)
            try:
                latest_frame_data = queue_frame_in.get_nowait()
            except queue.Empty:
                pass

            # Check for new audio (blocking with timeout)
            try:
                audio_data = queue_audio_in.get(timeout=0.5)
            except queue.Empty:
                continue

            if latest_frame_data is None:
                print("[Intent Parser] Warning: No frame data available yet.")
                continue

            print(f"[Intent Parser] Processing: {audio_data.text}")

            try:
                classifier_response = classify_intent(
                    audio_data.text, latest_frame_data.available_objects
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
                queue_out.put(intent_data)
                print(f"[Intent Parser] Generated {len(commands)} command(s).")
            except Exception as e:
                print(f"[Intent Parser] Failed to parse intent: {e}")
                announce_status(f"Intent parsing failed: {e}")

    except Exception as e:
        print(f"[Intent Parser] Error: {e}")
        stop_event.set()
