"""
Data classes for thread communication in the robot brain.
"""
from dataclasses import dataclass
from typing import Any


@dataclass
class FrameData:
    """Carries frame and detection data between threads."""
    frame: Any
    detections: list[dict[str, Any]]
    available_objects: list[str]
    timestamp: float


@dataclass
class AudioData:
    """Carries transcribed audio data."""
    text: str
    timestamp: float


@dataclass
class IntentData:
    """Carries parsed intent and commands."""
    classifier_response: Any
    commands: list[dict[str, Any]]
    detections: list[dict[str, Any]]
    frame_shape: tuple[int, int, int]
    timestamp: float


@dataclass
class TaskData:
    """Carries task plan for robot execution."""
    task_queue: list[dict[str, Any]]
    timestamp: float
