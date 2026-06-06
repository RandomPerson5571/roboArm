import sys
import os
from pathlib import Path

# Add the brain directory to the path so imports work correctly
BRAIN_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BRAIN_DIR))

import pytest


@pytest.fixture
def mock_yolo_model():
    """Fixture providing a mock YOLO model"""
    from unittest.mock import MagicMock
    model = MagicMock()
    model.track.return_value = [MagicMock()]
    return model


@pytest.fixture
def mock_camera():
    """Fixture providing a mock camera object"""
    from unittest.mock import MagicMock
    camera = MagicMock()
    camera.isOpened.return_value = True
    camera.read.return_value = (True, MagicMock())
    return camera


@pytest.fixture
def mock_arduino():
    """Fixture providing a mock Arduino serial connection"""
    from unittest.mock import MagicMock
    arduino = MagicMock()
    arduino.write = MagicMock()
    arduino.readline = MagicMock(return_value=b'{}')
    return arduino


@pytest.fixture
def sample_task_plan():
    """Fixture providing a sample task plan"""
    return {
        "task": "pick_up_object",
        "steps": [
            {"type": "move", "x": 50, "y": 30, "z": 100},
            {"type": "gripper", "state": "close", "grip_strength": 75},
            {"type": "move", "x": 0, "y": 0, "z": 100},
        ]
    }


@pytest.fixture
def sample_detection():
    """Fixture providing a sample object detection"""
    return {
        "name": "cup",
        "bbox": (100, 150, 200, 250),
        "center_x": 150,
        "center_y": 200,
    }


@pytest.fixture
def sample_frame_shape():
    """Fixture providing a sample frame shape"""
    return (480, 640, 3)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow")


# Optional: Add test discovery pattern
pytest_plugins = []
