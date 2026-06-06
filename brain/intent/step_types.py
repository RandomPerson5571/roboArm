from typing import Literal, TypedDict
from dataclasses import dataclass

class MoveStep(TypedDict):
    type: Literal["move"]
    x: float
    y: float
    z: float

class GripperStep(TypedDict):
    type: Literal["gripper"]
    state: Literal["open", "close"]
    grip_strength: float | None

class HomeStep(TypedDict):
    type: Literal["home"]


class StopStep(TypedDict):
    type: Literal["stop"]


Step = MoveStep | GripperStep | HomeStep | StopStep

@dataclass
class TaskPlan(TypedDict):
    task: str
    steps: list[Step]