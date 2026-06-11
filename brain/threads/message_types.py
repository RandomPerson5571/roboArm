"""
Data classes for thread communication in the robot brain.
"""
from dataclasses import dataclass
import threading
from typing import Any


@dataclass
class FrameData:
    """Carries frame and detection data between threads."""
    frame: Any
    detections: list[dict[str, Any]]
    available_objects: list[str]
    timestamp: float


class LatestFrameState:
    """Thread-safe holder for the newest camera frame and detections."""

    def __init__(self) -> None:
        self._frame_data: FrameData | None = None
        self._lock = threading.Lock()

    def update(self, frame_data: FrameData) -> None:
        with self._lock:
            self._frame_data = frame_data

    def get(self) -> FrameData | None:
        with self._lock:
            return self._frame_data


@dataclass
class IntentData:
    """Carries parsed intent and commands."""
    classifier_response: Any
    commands: list[dict[str, Any]]
    detections: list[dict[str, Any]]
    frame_shape: tuple[int, int, int]
    timestamp: float
