import pytest
import json
from unittest.mock import patch, MagicMock
from brain.arduino.seralizer import get_arduino, send_json_data, wait_for_arduino
from planner.step_types import TaskPlan

class TestGetArduino:
    @patch('arduino.serial.serial')
    @patch('arduino.serial.time')
    def test_get_arduino_default_port(self, mock_time_module, mock_serial_module):
        mock_arduino = MagicMock()
        mock_serial_module.Serial.return_value = mock_arduino
        
        result = get_arduino()
        
        mock_serial_module.Serial.assert_called_once_with(port='COM3', baudrate=115200, timeout=1)
        mock_time_module.sleep.assert_called_once_with(2)
        assert result == mock_arduino

    @patch('arduino.serial.serial')
    @patch('arduino.serial.time')
    def test_get_arduino_custom_port(self, mock_time_module, mock_serial_module):
        mock_arduino = MagicMock()
        mock_serial_module.Serial.return_value = mock_arduino
        
        result = get_arduino(port='COM5')
        
        mock_serial_module.Serial.assert_called_once_with(port='COM5', baudrate=115200, timeout=1)

    @patch('arduino.serial.serial')
    @patch('arduino.serial.time')
    def test_get_arduino_waits_for_reset(self, mock_time_module, mock_serial_module):
        mock_arduino = MagicMock()
        mock_serial_module.Serial.return_value = mock_arduino
        
        get_arduino()
        
        mock_time_module.sleep.assert_called_once_with(2)


class TestSendJsonData:
    def test_send_json_data_basic(self, capsys):
        mock_arduino = MagicMock()
        task_plan: TaskPlan = {
            "task": "pick_up_object",
            "steps": [
                {"type": "move", "x": 50, "y": 30, "z": 100}
            ]
        }
        
        send_json_data(mock_arduino, task_plan)
        
        # Verify JSON was sent
        expected_json = json.dumps(task_plan) + "\n"
        mock_arduino.write.assert_called_once_with(expected_json.encode('utf-8'))
        mock_arduino.close.assert_called_once()

    def test_send_json_data_with_gripper_step(self, capsys):
        mock_arduino = MagicMock()
        task_plan: TaskPlan = {
            "task": "pick_up_object",
            "steps": [
                {"type": "move", "x": 50, "y": 30, "z": 100},
                {"type": "gripper", "state": "close", "grip_strength": 75}
            ]
        }
        
        send_json_data(mock_arduino, task_plan)
        
        call_args = mock_arduino.write.call_args[0][0]
        decoded = call_args.decode('utf-8').strip()
        parsed = json.loads(decoded)
        
        assert len(parsed["steps"]) == 2
        assert parsed["steps"][1]["state"] == "close"

    def test_send_json_data_prints_message(self, capsys):
        mock_arduino = MagicMock()
        task_plan: TaskPlan = {
            "task": "test",
            "steps": []
        }
        
        send_json_data(mock_arduino, task_plan)
        
        captured = capsys.readouterr()
        assert "Sent:" in captured.out

    def test_send_json_data_closes_connection(self, capsys):
        mock_arduino = MagicMock()
        task_plan: TaskPlan = {
            "task": "test",
            "steps": []
        }
        
        send_json_data(mock_arduino, task_plan)
        
        mock_arduino.close.assert_called_once()

    def test_send_json_data_drop_off(self, capsys):
        mock_arduino = MagicMock()
        task_plan: TaskPlan = {
            "task": "drop_off_object",
            "steps": [
                {"type": "move", "x": 60, "y": 40, "z": 50},
                {"type": "gripper", "state": "open", "grip_strength": None}
            ]
        }
        
        send_json_data(mock_arduino, task_plan)
        
        call_args = mock_arduino.write.call_args[0][0]
        decoded = call_args.decode('utf-8').strip()
        parsed = json.loads(decoded)
        
        assert parsed["task"] == "drop_off_object"
        assert parsed["steps"][1]["grip_strength"] is None

    def test_send_json_data_home_step(self, capsys):
        mock_arduino = MagicMock()
        task_plan: TaskPlan = {
            "task": "go_home",
            "steps": [
                {"type": "move", "x": 0, "y": 0, "z": 100},
                {"type": "home"}
            ]
        }
        
        send_json_data(mock_arduino, task_plan)
        
        call_args = mock_arduino.write.call_args[0][0]
        decoded = call_args.decode('utf-8').strip()
        parsed = json.loads(decoded)
        
        assert any(step["type"] == "home" for step in parsed["steps"])


class TestWaitForArduino:
    @patch('arduino.serial.json')
    def test_wait_for_arduino_valid_response(self, mock_json_module):
        mock_arduino = MagicMock()
        expected_response = {"status": "success", "message": "Task completed"}
        mock_arduino.readline.return_value = b'{"status": "success"}'
        mock_json_module.load.return_value = expected_response
        
        result = wait_for_arduino(mock_arduino)
        
        assert result == expected_response
        mock_arduino.readline.assert_called_once()
        mock_json_module.load.assert_called_once()

    @patch('arduino.serial.json')
    def test_wait_for_arduino_error_response(self, mock_json_module):
        mock_arduino = MagicMock()
        error_response = {"status": "error", "error": "Invalid command"}
        mock_arduino.readline.return_value = b'{"status": "error"}'
        mock_json_module.load.return_value = error_response
        
        result = wait_for_arduino(mock_arduino)
        
        assert result["status"] == "error"
        mock_json_module.load.assert_called_once()

    @patch('arduino.serial.json')
    def test_wait_for_arduino_complex_response(self, mock_json_module):
        mock_arduino = MagicMock()
        complex_response = {
            "status": "success",
            "data": {
                "position": {"x": 50, "y": 30, "z": 100},
                "gripper": "closed"
            }
        }
        mock_arduino.readline.return_value = b'complex_json'
        mock_json_module.load.return_value = complex_response
        
        result = wait_for_arduino(mock_arduino)
        
        assert result["data"]["position"]["x"] == 50
        mock_json_module.load.assert_called_once()


class TestSerialIntegration:
    @patch('arduino.serial.json')
    @patch('arduino.serial.time')
    @patch('arduino.serial.serial')
    def test_full_send_and_wait_workflow(self, mock_serial_module, mock_time_module, mock_json_module):
        mock_arduino = MagicMock()
        mock_serial_module.Serial.return_value = mock_arduino
        
        # Get Arduino
        arduino = get_arduino('COM4')
        assert arduino == mock_arduino
        
        # Send data
        task_plan: TaskPlan = {
            "task": "pick_up_object",
            "steps": [
                {"type": "move", "x": 50, "y": 30, "z": 100}
            ]
        }
        
        send_json_data(arduino, task_plan)
        mock_arduino.write.assert_called_once()
        
        # Wait for response
        mock_arduino.readline.return_value = b'{"status": "success"}'
        mock_json_module.load.return_value = {"status": "success"}
        
        response = wait_for_arduino(mock_arduino)
        assert response["status"] == "success"
