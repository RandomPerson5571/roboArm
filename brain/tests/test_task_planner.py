import pytest
from unittest.mock import patch, MagicMock
from planner.task_planner import task_planner
from planner.step_types import TaskPlan
from planner.schema import Intent

class TestTaskPlannerPickUp:
    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_pick_up_valid(self):
        result = task_planner(Intent.PICK_UP, x=50, y=30, z=100, grip_strength=75)
        
        assert result["task"] == "pick_up_object"
        assert len(result["steps"]) == 3
        assert result["steps"][0]["type"] == "move"
        assert result["steps"][1]["type"] == "gripper"
        assert result["steps"][1]["state"] == "close"
        assert result["steps"][1]["grip_strength"] == 75
        assert result["steps"][2]["type"] == "move"

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_pick_up_missing_x(self):
        with pytest.raises(ValueError, match="pick_up requires"):
            task_planner(Intent.PICK_UP, y=30, z=100, grip_strength=75)

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_pick_up_missing_y(self):
        with pytest.raises(ValueError, match="pick_up requires"):
            task_planner(Intent.PICK_UP, x=50, z=100, grip_strength=75)

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_pick_up_missing_z(self):
        with pytest.raises(ValueError, match="pick_up requires"):
            task_planner(Intent.PICK_UP, x=50, y=30, grip_strength=75)

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_pick_up_missing_grip_strength(self):
        with pytest.raises(ValueError, match="pick_up requires"):
            task_planner(Intent.PICK_UP, x=50, y=30, z=100)

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_pick_up_returns_to_home(self):
        result = task_planner(Intent.PICK_UP, x=50, y=30, z=100, grip_strength=75)
        
        home_step = result["steps"][-1]
        assert home_step["x"] == 0
        assert home_step["y"] == 0
        assert home_step["z"] == 100

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_pick_up_with_zero_coordinates(self):
        result = task_planner(Intent.PICK_UP, x=0, y=0, z=0, grip_strength=50)
        
        assert result["steps"][0]["x"] == 0
        assert result["steps"][0]["y"] == 0
        assert result["steps"][0]["z"] == 0

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_pick_up_with_negative_coordinates(self):
        result = task_planner(Intent.PICK_UP, x=-50, y=-30, z=100, grip_strength=60)
        
        assert result["steps"][0]["x"] == -50
        assert result["steps"][0]["y"] == -30

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_pick_up_with_float_coordinates(self):
        result = task_planner(Intent.PICK_UP, x=50.5, y=30.25, z=100.75, grip_strength=75)
        
        assert result["steps"][0]["x"] == 50.5
        assert result["steps"][0]["y"] == 30.25
        assert result["steps"][0]["z"] == 100.75

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_pick_up_grip_strength_variations(self):
        for grip in [10, 25, 50, 75, 100]:
            result = task_planner(Intent.PICK_UP, x=50, y=30, z=100, grip_strength=grip)
            assert result["steps"][1]["grip_strength"] == grip


class TestTaskPlannerDropOff:
    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_drop_off_valid(self):
        result = task_planner(Intent.DROP_OFF, x=50, y=30, z=100)
        
        assert result["task"] == "drop_off_object"
        assert len(result["steps"]) == 3
        assert result["steps"][1]["type"] == "gripper"
        assert result["steps"][1]["state"] == "open"

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_drop_off_missing_x(self):
        with pytest.raises(ValueError, match="drop_off requires"):
            task_planner(Intent.DROP_OFF, y=30, z=100)

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_drop_off_missing_y(self):
        with pytest.raises(ValueError, match="drop_off requires"):
            task_planner(Intent.DROP_OFF, x=50, z=100)

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_drop_off_missing_z(self):
        with pytest.raises(ValueError, match="drop_off requires"):
            task_planner(Intent.DROP_OFF, x=50, y=30)

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_drop_off_returns_to_home(self):
        result = task_planner(Intent.DROP_OFF, x=50, y=30, z=100)
        
        home_step = result["steps"][-1]
        assert home_step["x"] == 0
        assert home_step["y"] == 0

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_drop_off_gripper_open_no_strength(self):
        result = task_planner(Intent.DROP_OFF, x=60, y=40, z=50)
        
        gripper_step = result["steps"][1]
        assert gripper_step["state"] == "open"

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_drop_off_with_negative_coordinates(self):
        result = task_planner(Intent.DROP_OFF, x=-50, y=-30, z=50)
        
        assert result["steps"][0]["x"] == -50
        assert result["steps"][0]["y"] == -30


class TestTaskPlannerMoveTo:
    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_move_to_valid(self):
        result = task_planner(Intent.MOVE_TO, x=50, y=30, z=100)
        
        assert result["task"] == "move_to_position"
        assert len(result["steps"]) == 1
        assert result["steps"][0]["x"] == 50
        assert result["steps"][0]["y"] == 30
        assert result["steps"][0]["z"] == 100

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_move_to_missing_x(self):
        with pytest.raises(ValueError, match="move_to requires"):
            task_planner(Intent.MOVE_TO, y=30, z=100)

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_move_to_missing_y(self):
        with pytest.raises(ValueError, match="move_to requires"):
            task_planner(Intent.MOVE_TO, x=50, z=100)

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_move_to_missing_z(self):
        with pytest.raises(ValueError, match="move_to requires"):
            task_planner(Intent.MOVE_TO, x=50, y=30)

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_move_to_no_return_home(self):
        result = task_planner(Intent.MOVE_TO, x=50, y=30, z=100)
        
        # Move_to should only have one step, no return to home
        assert len(result["steps"]) == 1


class TestTaskPlannerHome:
    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_home_action(self):
        result = task_planner(Intent.HOME)
        
        assert result["task"] == "go_home"
        assert len(result["steps"]) == 1
        assert result["steps"][0]["type"] == "move"
        assert result["steps"][0]["x"] == 0
        assert result["steps"][0]["y"] == 0
        assert result["steps"][0]["z"] == 100

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_home_ignores_parameters(self):
        # Home should ignore any parameters passed
        result = task_planner(Intent.HOME, x=50, y=30, z=100, grip_strength=75)
        
        assert result["task"] == "go_home"
        assert result["steps"][0]["x"] == 0


class TestTaskPlannerStop:
    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_stop_action(self):
        result = task_planner(Intent.STOP)
        
        assert result["task"] == "emergency_stop"
        assert len(result["steps"]) == 1
        assert result["steps"][0]["type"] == "stop"

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_stop_ignores_parameters(self):
        # Stop should ignore any parameters passed
        result = task_planner(Intent.STOP, x=50, y=30)
        
        assert result["task"] == "emergency_stop"


class TestTaskPlannerWave:
    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_wave_action(self):
        result = task_planner(Intent.WAVE)
        
        assert result["task"] == "wave"
        assert len(result["steps"]) == 6
        
        # Check move steps
        assert result["steps"][0]["type"] == "move"
        assert result["steps"][1]["type"] == "move"
        
        # Check final home step
        assert result["steps"][-1]["type"] == "home"

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_wave_movement_pattern(self):
        result = task_planner(Intent.WAVE)
        
        # Verify wave motion coordinates
        assert result["steps"][0]["x"] == 50
        assert result["steps"][1]["x"] == 80
        assert result["steps"][2]["x"] == 80

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_wave_z_coordinate(self):
        result = task_planner(Intent.WAVE)
        
        # All move steps should have z=120
        for step in result["steps"][:-1]:
            if step["type"] == "move":
                assert step["z"] == 120

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_wave_y_variations(self):
        result = task_planner(Intent.WAVE)
        
        # Check that y varies for waving motion
        y_values = [step["y"] for step in result["steps"][:5] if step["type"] == "move"]
        assert len(set(y_values)) > 1  # Should have different y values

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_wave_ignores_parameters(self):
        result = task_planner(Intent.WAVE, x=100, y=100, z=200, grip_strength=100)
        
        assert result["task"] == "wave"
        # Should still have the predefined wave pattern
        assert result["steps"][0]["x"] == 50


class TestTaskPlannerIntegration:
    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_all_intents_return_task_plan(self):
        for intent in [Intent.PICK_UP, Intent.DROP_OFF, Intent.MOVE_TO, Intent.HOME, Intent.STOP, Intent.WAVE]:
            if intent in [Intent.PICK_UP, Intent.DROP_OFF, Intent.MOVE_TO]:
                result = task_planner(intent, x=50, y=30, z=100, grip_strength=75)
            else:
                result = task_planner(intent)
            
            assert isinstance(result, dict)
            assert "task" in result
            assert "steps" in result
            assert isinstance(result["steps"], list)

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_task_plan_structure(self):
        result = task_planner(Intent.PICK_UP, x=50, y=30, z=100, grip_strength=75)
        
        # Check all steps have required fields
        for step in result["steps"]:
            assert "type" in step
            assert step["type"] in ["move", "gripper", "home", "stop"]

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_move_step_structure(self):
        result = task_planner(Intent.MOVE_TO, x=50, y=30, z=100)
        
        step = result["steps"][0]
        assert step["type"] == "move"
        assert step["x"] == 50
        assert step["y"] == 30
        assert step["z"] == 100

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_gripper_step_structure(self):
        result = task_planner(Intent.PICK_UP, x=50, y=30, z=100, grip_strength=75)
        
        step = result["steps"][1]
        assert step["type"] == "gripper"
        assert step["state"] in ["open", "close"]
        assert "grip_strength" in step


class TestTaskPlannerEdgeCases:
    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_large_coordinates(self):
        result = task_planner(Intent.MOVE_TO, x=9999, y=9999, z=9999)
        
        assert result["steps"][0]["x"] == 9999
        assert result["steps"][0]["y"] == 9999
        assert result["steps"][0]["z"] == 9999

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_very_small_coordinates(self):
        result = task_planner(Intent.MOVE_TO, x=0.001, y=0.001, z=0.001)
        
        assert result["steps"][0]["x"] == 0.001
        assert result["steps"][0]["y"] == 0.001

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_pick_up_minimum_grip_strength(self):
        result = task_planner(Intent.PICK_UP, x=50, y=30, z=100, grip_strength=10)
        
        assert result["steps"][1]["grip_strength"] == 10

    @patch('planner.task_planner.TOOL_CONFIG', {'ROBOT_HOME_POSITION': (0, 0, 100)})
    def test_pick_up_maximum_grip_strength(self):
        result = task_planner(Intent.PICK_UP, x=50, y=30, z=100, grip_strength=100)
        
        assert result["steps"][1]["grip_strength"] == 100
