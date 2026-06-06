from __future__ import annotations

from config import TOOL_CONFIG

from intent.step_types import TaskPlan
from intent.schema import Intent

HOME_POSITION = TOOL_CONFIG["ROBOT_HOME_POSITION"] or (0, 0, 100)

def task_planner(intent: Intent, *, x: float | None = None, y: float | None = None, z: float | None = None, grip_strength: float | None = None) -> TaskPlan:
    match intent:
        case Intent.PICK_UP:
            if x is None or y is None or z is None or grip_strength is None:
                raise ValueError("pick_up requires x, y, z or grip_strength")

            return {
                "task": "pick_up_object",
                "steps": [
                    {"type": "move", "x": x, "y": y, "z": z},
                    {"type": "gripper", "state": "close", "grip_strength": grip_strength},
                    {
                        "type": "move",
                        "x": HOME_POSITION[0],
                        "y": HOME_POSITION[1],
                        "z": HOME_POSITION[2],
                    },
                ],
            }

        case Intent.DROP_OFF:
            if x is None or y is None or z is None:
                raise ValueError("drop_off requires x, y, z")

            return {
                "task": "drop_off_object",
                "steps": [
                    {"type": "move", "x": x, "y": y, "z": z},
                    {"type": "gripper", "state": "open"},
                    {
                        "type": "move",
                        "x": HOME_POSITION[0],
                        "y": HOME_POSITION[1],
                        "z": HOME_POSITION[2],
                    },
                ],
            }

        case Intent.MOVE_TO:
            if x is None or y is None or z is None:
                raise ValueError("move_to requires x, y, z")

            return {
                "task": "move_to_position",
                "steps": [
                    {"type": "move", "x": x, "y": y, "z": z},
                ],
            }

        case Intent.HOME:
            return {
                "task": "go_home",
                "steps": [
                    {
                        "type": "move",
                        "x": HOME_POSITION[0],
                        "y": HOME_POSITION[1],
                        "z": HOME_POSITION[2],
                    },
                ],
            }

        case Intent.STOP:
            return {
                "task": "emergency_stop",
                "steps": [
                    {"type": "stop"},
                ],
            }

        case Intent.WAVE:
            return {
                "task": "wave",
                "steps": [
                    {"type": "move", "x": 50, "y": 0, "z": 120},
                    {"type": "move", "x": 80, "y": 20, "z": 120},
                    {"type": "move", "x": 80, "y": -20, "z": 120},
                    {"type": "move", "x": 80, "y": 20, "z": 120},
                    {"type": "move", "x": 80, "y": -20, "z": 120},
                    {"type": "home"},
                ],
            }