"""
Task plan building from intent and commands.
"""
from typing import Any

from config import TOOL_CONFIG
from intent.task_planner import task_planner
from intent.schema import Intent, RobotIntents
from camera.camera import bounding_box_to_robot_position


def build_task_plan(
    command: dict[str, Any],
    detections: list[dict[str, Any]],
    frame_shape: tuple[int, int, int],
) -> dict[str, Any]:
    """
    Build a task plan from a command using intent schema and vision detections.
    
    Args:
        command: Command dictionary with action and optional coordinates
        detections: List of detected objects from vision
        frame_shape: Shape of the camera frame
        
    Returns:
        Task plan dictionary ready for robot execution
        
    Raises:
        ValueError: If command is invalid or coordinates cannot be determined
    """
    action_name = command.get("action")
    if not action_name:
        raise ValueError("Classifier command missing 'action'.")

    try:
        RobotIntents(action_name)
    except ValueError:
        raise ValueError(f"Unsupported robot intent: {action_name}")

    intent = Intent(action_name)
    x = command.get("x")
    y = command.get("y")
    z = command.get("z")
    grip_strength = command.get("grip_strength", 50)
    target_object = command.get("target_object")

    if target_object != "no_object":
        match = next((item for item in detections if item["name"] == target_object), None)
        if match is None:
            raise ValueError(f"Target object '{target_object}' not detected by vision.")
        x, y, z = bounding_box_to_robot_position(match["bbox"], frame_shape)

    if z is None:
        z = TOOL_CONFIG.get("ROBOT_DEFAULT_Z") or 50

    if intent in {Intent.PICK_UP, Intent.DROP_OFF, Intent.MOVE_TO}:
        if x is None or y is None or z is None:
            raise ValueError("Movement commands require target_object detection or explicit coordinates.")

    return task_planner(
        intent,
        x=x,
        y=y,
        z=z,
        grip_strength=grip_strength,
    )
