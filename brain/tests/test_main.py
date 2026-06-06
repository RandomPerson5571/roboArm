import pytest
import json
from unittest.mock import patch, MagicMock, call
from main import (
    announce_status,
    parse_classifier_response,
    extract_primary_command,
    extract_commands_from_payload,
    build_task_plan,
)
from planner.schema import Intent


class TestAnnounceStatus:
    def test_announce_status_prints_message(self, capsys):
        message = "Robot moving forward"
        announce_status(message)
        captured = capsys.readouterr()
        assert message in captured.out

    @patch('main.announce_actions')
    def test_announce_status_calls_announce_actions(self, mock_announce):
        message = "Test announcement"
        announce_status(message)
        mock_announce.assert_called_once_with(message)

    @patch('main.announce_actions')
    def test_announce_status_with_empty_string(self, mock_announce, capsys):
        announce_status("")
        captured = capsys.readouterr()
        mock_announce.assert_called_once_with("")


class TestParseClassifierResponse:
    def test_parse_dict_response(self):
        response = {"action": "pick_up", "target_object": "cup"}
        result = parse_classifier_response(response)
        assert result == response

    def test_parse_valid_json_string(self):
        response = '{"action": "pick_up", "target_object": "cup"}'
        result = parse_classifier_response(response)
        assert result == {"action": "pick_up", "target_object": "cup"}

    def test_parse_json_with_whitespace(self):
        response = '  {"action": "drop_off"}  '
        result = parse_classifier_response(response)
        assert result == {"action": "drop_off"}

    def test_parse_json_embedded_in_text(self):
        response = 'Some text before {"action": "move_to"} some text after'
        result = parse_classifier_response(response)
        assert result == {"action": "move_to"}

    def test_parse_json_array_embedded(self):
        response = 'Here is the command: [{"action": "home"}]'
        result = parse_classifier_response(response)
        assert result == [{"action": "home"}]

    def test_parse_invalid_json_raises_error(self):
        response = "This is not JSON at all"
        with pytest.raises(ValueError, match="Could not parse classifier response as JSON"):
            parse_classifier_response(response)

    def test_parse_malformed_json_string(self):
        response = '{"action": "pick_up", "incomplete": '
        with pytest.raises(ValueError):
            parse_classifier_response(response)


class TestExtractPrimaryCommand:
    def test_extract_from_list(self):
        payload = [{"action": "pick_up", "target_object": "cup"}]
        result = extract_primary_command(payload)
        assert result == {"action": "pick_up", "target_object": "cup"}

    def test_extract_from_dict_with_commands(self):
        payload = {
            "commands": [
                {"action": "pick_up"},
                {"action": "move_to"}
            ]
        }
        result = extract_primary_command(payload)
        assert result == {"action": "pick_up"}

    def test_extract_from_dict_with_action(self):
        payload = {"action": "home"}
        result = extract_primary_command(payload)
        assert result == payload

    def test_extract_empty_list_raises_error(self):
        with pytest.raises(ValueError, match="does not contain a valid command"):
            extract_primary_command([])

    def test_extract_dict_without_commands_or_action_raises_error(self):
        with pytest.raises(ValueError):
            extract_primary_command({"target_object": "cup"})

    def test_extract_invalid_type_raises_error(self):
        with pytest.raises(ValueError):
            extract_primary_command("invalid")


class TestExtractCommandsFromPayload:
    def test_extract_from_list(self):
        payload = [
            {"action": "pick_up", "target_object": "cup"},
            {"action": "move_to", "x": 10, "y": 20, "z": 30},
        ]
        result = extract_commands_from_payload(payload)
        assert result == payload

    def test_extract_from_dict_with_commands(self):
        payload = {
            "commands": [
                {"action": "pick_up"},
                {"action": "move_to"},
            ]
        }
        result = extract_commands_from_payload(payload)
        assert result == payload["commands"]

    def test_extract_single_action_dict(self):
        payload = {"action": "home"}
        result = extract_commands_from_payload(payload)
        assert result == [payload]

    def test_extract_empty_list_raises_error(self):
        with pytest.raises(ValueError, match="empty command list"):
            extract_commands_from_payload([])

    def test_extract_invalid_dict_raises_error(self):
        with pytest.raises(ValueError):
            extract_commands_from_payload({"target_object": "cup"})


class TestBuildTaskPlan:
    @patch('main.bounding_box_to_robot_position')
    def test_build_pick_up_with_coordinates(self, mock_bbox):
        command = {
            "action": "pick_up",
            "x": 50,
            "y": 30,
            "z": 100,
            "grip_strength": 75
        }
        detections = []
        frame_shape = (480, 640, 3)
        
        result = build_task_plan(command, detections, frame_shape)
        
        assert result["task"] == "pick_up_object"
        assert len(result["steps"]) == 3
        assert result["steps"][0]["type"] == "move"
        assert result["steps"][1]["type"] == "gripper"
        assert result["steps"][1]["state"] == "close"

    @patch('main.bounding_box_to_robot_position')
    def test_build_pick_up_with_object_detection(self, mock_bbox):
        mock_bbox.return_value = (45, 25, 100)
        
        command = {
            "action": "pick_up",
            "target_object": "cup",
            "grip_strength": 60
        }
        detections = [{"name": "cup", "bbox": (100, 150, 200, 250)}]
        frame_shape = (480, 640, 3)
        
        result = build_task_plan(command, detections, frame_shape)
        
        assert result["task"] == "pick_up_object"
        mock_bbox.assert_called_once()

    @patch('main.bounding_box_to_robot_position')
    def test_build_drop_off(self, mock_bbox):
        command = {
            "action": "drop_off",
            "x": 60,
            "y": 40,
            "z": 50
        }
        detections = []
        frame_shape = (480, 640, 3)
        
        result = build_task_plan(command, detections, frame_shape)
        
        assert result["task"] == "drop_off_object"
        assert result["steps"][1]["state"] == "open"

    @patch('main.bounding_box_to_robot_position')
    def test_build_move_to(self, mock_bbox):
        command = {
            "action": "move_to",
            "x": 70,
            "y": 50,
            "z": 90
        }
        detections = []
        frame_shape = (480, 640, 3)
        
        result = build_task_plan(command, detections, frame_shape)
        
        assert result["task"] == "move_to_position"
        assert len(result["steps"]) == 1

    @patch('main.bounding_box_to_robot_position')
    def test_build_task_plan_missing_action(self, mock_bbox):
        command = {"x": 50, "y": 30}
        detections = []
        frame_shape = (480, 640, 3)
        
        with pytest.raises(ValueError, match="missing 'action'"):
            build_task_plan(command, detections, frame_shape)

    @patch('main.bounding_box_to_robot_position')
    def test_build_pick_up_missing_coordinates(self, mock_bbox):
        command = {"action": "pick_up", "grip_strength": 50}
        detections = []
        frame_shape = (480, 640, 3)
        
        with pytest.raises(ValueError, match="Movement commands require"):
            build_task_plan(command, detections, frame_shape)

    @patch('main.bounding_box_to_robot_position')
    def test_build_task_plan_object_not_detected(self, mock_bbox):
        command = {
            "action": "pick_up",
            "target_object": "apple",
            "grip_strength": 50
        }
        detections = [{"name": "cup", "bbox": (100, 150, 200, 250)}]
        frame_shape = (480, 640, 3)
        
        with pytest.raises(ValueError, match="Target object 'apple' not detected"):
            build_task_plan(command, detections, frame_shape)

    @patch('main.bounding_box_to_robot_position')
    @patch('main.TOOL_CONFIG', {'ROBOT_DEFAULT_Z': 75})
    def test_build_task_with_default_z(self, mock_bbox):
        command = {
            "action": "move_to",
            "x": 50,
            "y": 30,
        }
        detections = []
        frame_shape = (480, 640, 3)
        
        result = build_task_plan(command, detections, frame_shape)
        assert result["steps"][0]["z"] == 75
