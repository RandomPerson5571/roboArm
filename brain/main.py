import time
import threading
import queue

import cv2

from config import TOOL_CONFIG
from arduino.seralizer import get_arduino
from camera.camera import create_detector
from speech.text_to_speech import announce_status
from threads import (
    LatestFrameState,
    camera_thread_worker,
    command_thread_worker,
)


def main() -> None:
    """
    Main coordinator thread that spawns and manages 2 worker threads:
    1. Camera + YOLO detection
    2. Voice command processing + robot state machine
    """
    print("\n" + "=" * 70)
    print("Robot Brain Starting - Multi-threaded Architecture")
    print("=" * 70)

    # Initialize camera and model once
    try:
        model = create_detector()
        print("[Main] YOLO model loaded.")
    except Exception as e:
        print(f"[Main] Failed to load YOLO model: {e}")
        return

    # Arduino initialization (commented out if not available)
    arduino = None
    try:
        serial_port = TOOL_CONFIG.get("SERIAL_PORT", "COM3")
        arduino = get_arduino(serial_port)
        print(f"[Main] Arduino connected on {serial_port}.")
    except Exception as e:
        print(f"[Main] Arduino connection failed: {e}")

    # Share only the newest camera result so command processing never uses stale frames.
    latest_frame_state = LatestFrameState()
    command_control_queue = queue.Queue()

    # Shared stop event for graceful shutdown
    stop_event = threading.Event()

    # Create and start worker threads
    threads = [
        threading.Thread(
            name="Camera",
            target=camera_thread_worker,
            args=(latest_frame_state, stop_event, model),
            daemon=False,
        ),
        threading.Thread(
            name="CommandProcessor",
            target=command_thread_worker,
            args=(command_control_queue, latest_frame_state, stop_event, arduino),
            daemon=False,
        ),
    ]

    def input_thread_worker(control_queue: queue.Queue, stop_event: threading.Event) -> None:
        """
        Background thread that reads user input and sends signals to control_queue.
        """
        try:
            while not stop_event.is_set():
                try:
                    user_input = input("Enter 'c' to capture speech, 'q' to quit: ").strip().lower()
                    if user_input == 'c':
                        control_queue.put("CAPTURE")
                        print("[Input] Microphone capture triggered.")
                    elif user_input == 'q':
                        print("[Input] Quit command received.")
                        stop_event.set()
                except EOFError:
                    break
                except Exception as e:
                    print(f"[Input] Error: {e}")
                    break
        except Exception as e:
            print(f"[Input] Fatal error: {e}")
            stop_event.set()

        
    for thread in threads:
        thread.start()
        print(f"[Main] Started {thread.name} thread.")

    # Start input thread
    input_thread = threading.Thread(
        name="InputHandler",
        target=input_thread_worker,
        args=(command_control_queue, stop_event),
        daemon=True,
    )
    input_thread.start()
    print("[Main] Started InputHandler thread.")

    announce_status("Robot brain online. Press 'c' to capture a voice command, or 'q' to exit.")

    # Main thread waits for stop_event
    try:
        while not stop_event.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[Main] Keyboard interrupt received.")
        stop_event.set()

    # Wait for all threads to finish
    print("[Main] Waiting for threads to finish...")
    for thread in threads:
        thread.join(timeout=5.0)
        if thread.is_alive():
            print(f"[Main] Warning: {thread.name} thread did not finish cleanly.")

    # Ensure OpenCV windows are closed even if the camera thread did not clean up fully.
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass

    print("[Main] All threads stopped. Robot brain offline.")
    print("=" * 70)

if __name__ == "__main__":
    main()
