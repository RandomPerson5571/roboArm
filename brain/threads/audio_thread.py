"""
Audio capture and transcription thread workers.
"""
import time
import threading
import queue

from speech.text_to_speech import announce_status
from speech.voice import capture_speech
from .message_types import AudioData


def microphone_thread_worker(
    queue_out: queue.Queue,
    control_queue: queue.Queue,
    stop_event: threading.Event,
) -> None:
    """
    Thread 2: Capture speech from microphone.
    Listens on control_queue for trigger signals, puts AudioData on queue_out when speech is detected.
    """
    try:
        while not stop_event.is_set():
            try:
                # Wait for trigger signal (with timeout to allow stop_event checking)
                signal = control_queue.get(timeout=0.5)
                if signal == "CAPTURE":
                    print("[Microphone] Capturing speech...")
                    voice_prompt = capture_speech()

                    if voice_prompt:
                        audio_data = AudioData(text=voice_prompt, timestamp=time.time())
                        queue_out.put(audio_data)
                        print(f"[Microphone] Captured: {voice_prompt}")
            except queue.Empty:
                continue
    except Exception as e:
        print(f"[Microphone] Error: {e}")
        stop_event.set()


def whisper_thread_worker(
    queue_in: queue.Queue,
    queue_out: queue.Queue,
    stop_event: threading.Event,
) -> None:
    """
    Thread 3: Transcribe audio (currently passes through since capture_speech
    already returns text, but kept for future Whisper integration).
    Consumes AudioData from queue_in, produces AudioData on queue_out.
    """
    try:
        while not stop_event.is_set():
            try:
                audio_data = queue_in.get(timeout=0.5)
            except queue.Empty:
                continue

            # Currently just pass-through; can integrate real Whisper here
            print(f"[Whisper] Processed: {audio_data.text}")
            queue_out.put(audio_data)
    except Exception as e:
        print(f"[Whisper] Error: {e}")
        stop_event.set()
