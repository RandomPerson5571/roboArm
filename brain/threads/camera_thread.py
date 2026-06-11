"""
Camera and YOLO detection thread worker.
"""
import time
import threading
from typing import Any

import cv2

from camera.camera import (
    detect_objects,
    open_camera,
    release_camera,
)
from config import TOOL_CONFIG
from .message_types import FrameData, LatestFrameState


def camera_thread_worker(
    latest_frame_state: LatestFrameState,
    stop_event: threading.Event,
    model: Any,
) -> None:
    """
    Continuously capture frames from camera and run YOLO detection.
    Publishes the newest FrameData to latest_frame_state.
    """
    try:
        camera_path = TOOL_CONFIG["CAMERA_PATH"]
        cap = open_camera(camera_path)

        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print("[Camera] Failed to grab frame.")
                time.sleep(0.01)
                continue

            detections, annotated_frame = detect_objects(frame, model)
            available_objects = sorted({d["name"] for d in detections})

            frame_data = FrameData(
                frame=frame,
                detections=detections,
                available_objects=available_objects,
                timestamp=time.time(),
            )
            latest_frame_state.update(frame_data)

            # Display the annotated frame
            cv2.imshow("Live Webcam Feed", annotated_frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
                stop_event.set()

        release_camera(cap)
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"[Camera] Error: {e}")
        stop_event.set()
