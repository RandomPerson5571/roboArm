import pytest
from typing import Optional
from intent.step_types import (
    MoveStep,
    GripperStep,
    HomeStep,
    StopStep,
    Step,
    TaskPlan,
)

from intent.schema import Intent

class TestIntentEnum:
    def test_intent_all_values(self):
        intents = [
            Intent.PICK_UP,
            Intent.DROP_OFF,
            Intent.MOVE_TO,
            Intent.HOME,
            Intent.STOP,
            Intent.WAVE,
        ]
        assert len(intents) == 6

    def test_intent_string_values(self):
        assert str(Intent.PICK_UP) == "pick_up"
        assert str(Intent.DROP_OFF) == "drop_off"
        assert str(Intent.MOVE_TO) == "move_to"
        assert str(Intent.HOME) == "home"
        assert str(Intent.STOP) == "stop"
        assert str(Intent.WAVE) == "wave"

    def test_intent_equality(self):
        assert Intent.PICK_UP == "pick_up"
        assert Intent.HOME == "home"


class TestMoveStep:
    def test_move_step_structure(self):
        step: MoveStep = {
            "type": "move",
            "x": 50.0,
            "y": 30.0,
            "z": 100.0,
        }
        assert step["type"] == "move"
        assert step["x"] == 50.0
        assert step["y"] == 30.0
        assert step["z"] == 100.0

    def test_move_step_with_negative_coordinates(self):
        step: MoveStep = {
            "type": "move",
            "x": -50.0,
            "y": -30.0,
            "z": 100.0,
        }
        assert step["x"] == -50.0
        assert step["y"] == -30.0

    def test_move_step_with_float_coordinates(self):
        step: MoveStep = {
            "type": "move",
            "x": 50.5,
            "y": 30.25,
            "z": 100.75,
        }
        assert step["x"] == 50.5
        assert step["y"] == 30.25
        assert step["z"] == 100.75

    def test_move_step_with_zero_coordinates(self):
        step: MoveStep = {
            "type": "move",
            "x": 0,
            "y": 0,
            "z": 0,
        }
        assert step["x"] == 0
        assert step["y"] == 0
        assert step["z"] == 0

    def test_move_step_type_is_string(self):
        step: MoveStep = {
            "type": "move",
            "x": 10,
            "y": 20,
            "z": 30,
        }
        assert isinstance(step["type"], str)
        assert step["type"] == "move"


class TestGripperStep:
    def test_gripper_step_close(self):
        step: GripperStep = {
            "type": "gripper",
            "state": "close",
            "grip_strength": 75.0,
        }
        assert step["type"] == "gripper"
        assert step["state"] == "close"
        assert step["grip_strength"] == 75.0

    def test_gripper_step_open(self):
        step: GripperStep = {
            "type": "gripper",
            "state": "open",
            "grip_strength": None,
        }
        assert step["state"] == "open"
        assert step["grip_strength"] is None

    def test_gripper_step_without_grip_strength(self):
        step: GripperStep = {
            "type": "gripper",
            "state": "open",
            "grip_strength": None,
        }
        assert step["grip_strength"] is None

    def test_gripper_step_with_zero_grip_strength(self):
        step: GripperStep = {
            "type": "gripper",
            "state": "close",
            "grip_strength": 0,
        }
        assert step["grip_strength"] == 0

    def test_gripper_step_with_high_grip_strength(self):
        step: GripperStep = {
            "type": "gripper",
            "state": "close",
            "grip_strength": 100,
        }
        assert step["grip_strength"] == 100


class TestHomeStep:
    def test_home_step_structure(self):
        step: HomeStep = {"type": "home"}
        assert step["type"] == "home"
        assert len(step) == 1

    def test_home_step_equality(self):
        step1: HomeStep = {"type": "home"}
        step2: HomeStep = {"type": "home"}
        assert step1 == step2


class TestStopStep:
    def test_stop_step_structure(self):
        step: StopStep = {"type": "stop"}
        assert step["type"] == "stop"
        assert len(step) == 1

    def test_stop_step_equality(self):
        step1: StopStep = {"type": "stop"}
        step2: StopStep = {"type": "stop"}
        assert step1 == step2


class TestTaskPlan:
    def test_task_plan_pick_up(self):
        plan: TaskPlan = {
            "task": "pick_up_object",
            "steps": [
                {"type": "move", "x": 50, "y": 30, "z": 100},
                {"type": "gripper", "state": "close", "grip_strength": 75},
                {"type": "move", "x": 0, "y": 0, "z": 100},
            ]
        }
        assert plan["task"] == "pick_up_object"
        assert len(plan["steps"]) == 3

    def test_task_plan_drop_off(self):
        plan: TaskPlan = {
            "task": "drop_off_object",
            "steps": [
                {"type": "move", "x": 50, "y": 30, "z": 100},
                {"type": "gripper", "state": "open", "grip_strength": None},
                {"type": "move", "x": 0, "y": 0, "z": 100},
            ]
        }
        assert plan["task"] == "drop_off_object"
        assert len(plan["steps"]) == 3

    def test_task_plan_move_to(self):
        plan: TaskPlan = {
            "task": "move_to_position",
            "steps": [
                {"type": "move", "x": 50, "y": 30, "z": 100},
            ]
        }
        assert plan["task"] == "move_to_position"
        assert len(plan["steps"]) == 1

    def test_task_plan_home(self):
        plan: TaskPlan = {
            "task": "go_home",
            "steps": [
                {"type": "move", "x": 0, "y": 0, "z": 100},
            ]
        }
        assert plan["task"] == "go_home"

    def test_task_plan_stop(self):
        plan: TaskPlan = {
            "task": "emergency_stop",
            "steps": [
                {"type": "stop"},
            ]
        }
        assert plan["task"] == "emergency_stop"

    def test_task_plan_wave(self):
        plan: TaskPlan = {
            "task": "wave",
            "steps": [
                {"type": "move", "x": 50, "y": 0, "z": 120},
                {"type": "move", "x": 80, "y": 20, "z": 120},
                {"type": "home"},
            ]
        }
        assert plan["task"] == "wave"
        assert len(plan["steps"]) >= 1

    def test_task_plan_empty_steps(self):
        plan: TaskPlan = {
            "task": "test",
            "steps": []
        }
        assert len(plan["steps"]) == 0

    def test_task_plan_with_multiple_steps(self):
        plan: TaskPlan = {
            "task": "complex_task",
            "steps": [
                {"type": "move", "x": 10, "y": 10, "z": 50},
                {"type": "gripper", "state": "close", "grip_strength": 50},
                {"type": "move", "x": 20, "y": 20, "z": 100},
                {"type": "gripper", "state": "open", "grip_strength": None},
                {"type": "home"},
            ]
        }
        assert len(plan["steps"]) == 5
        assert plan["steps"][0]["type"] == "move"
        assert plan["steps"][1]["type"] == "gripper"
        assert plan["steps"][-1]["type"] == "home"


class TestStepTypes:
    def test_step_can_be_move(self):
        step: Step = {
            "type": "move",
            "x": 50,
            "y": 30,
            "z": 100,
        }
        assert step["type"] == "move"

    def test_step_can_be_gripper(self):
        step: Step = {
            "type": "gripper",
            "state": "close",
            "grip_strength": 75,
        }
        assert step["type"] == "gripper"

    def test_step_can_be_home(self):
        step: Step = {"type": "home"}
        assert step["type"] == "home"

    def test_step_can_be_stop(self):
        step: Step = {"type": "stop"}
        assert step["type"] == "stop"
