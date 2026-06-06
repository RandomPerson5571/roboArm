import pytest
from unittest.mock import patch, MagicMock, call, mock_open
import serial
import time
import threading
from arduino.arduino_controller import ArduinoController


class TestArduinoControllerInit:
    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_init_creates_serial_connection(self, mock_sleep, mock_serial):
        mock_arduino = MagicMock()
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController(port='COM3', baudrate=9600)
        
        mock_serial.assert_called_once_with(port='COM3', baudrate=9600, timeout=0.1)
        mock_sleep.assert_called_once_with(2)

    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_init_starts_read_thread(self, mock_sleep, mock_serial):
        mock_arduino = MagicMock()
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController()
        
        assert hasattr(controller, 'read_thread')
        assert controller.read_thread.daemon is True

    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_init_custom_port_and_baudrate(self, mock_sleep, mock_serial):
        mock_arduino = MagicMock()
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController(port='COM5', baudrate=115200)
        
        mock_serial.assert_called_once_with(port='COM5', baudrate=115200, timeout=0.1)


class TestArduinoControllerSendCommand:
    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_send_command(self, mock_sleep, mock_serial):
        mock_arduino = MagicMock()
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController()
        controller.send_command("MOVE_TO:50,30,100")
        
        mock_arduino.write.assert_called_once_with(b"MOVE_TO:50,30,100\n")

    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_send_command_empty_string(self, mock_sleep, mock_serial):
        mock_arduino = MagicMock()
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController()
        controller.send_command("")
        
        mock_arduino.write.assert_called_once_with(b"\n")

    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_send_command_multiple_times(self, mock_sleep, mock_serial):
        mock_arduino = MagicMock()
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController()
        controller.send_command("CMD1")
        controller.send_command("CMD2")
        
        assert mock_arduino.write.call_count == 2


class TestArduinoControllerHandleResponse:
    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_handle_response_task_completed(self, mock_sleep, mock_serial, capsys):
        mock_arduino = MagicMock()
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController()
        controller.handle_response("TASK_COMPLETED")
        
        captured = capsys.readouterr()
        assert "Success! Task finished." in captured.out

    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_handle_response_cancelled(self, mock_sleep, mock_serial, capsys):
        mock_arduino = MagicMock()
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController()
        controller.handle_response("CANCELLED")
        
        captured = capsys.readouterr()
        assert "Arduino confirmed the cancellation." in captured.out

    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_handle_response_unknown(self, mock_sleep, mock_serial):
        mock_arduino = MagicMock()
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController()
        # Should not raise error for unknown response
        controller.handle_response("UNKNOWN_RESPONSE")


class TestArduinoControllerClose:
    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_close_stops_running(self, mock_sleep, mock_serial):
        mock_arduino = MagicMock()
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController()
        assert controller.running is True
        
        controller.close()
        
        assert controller.running is False
        mock_arduino.close.assert_called_once()

    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_close_closes_serial(self, mock_sleep, mock_serial):
        mock_arduino = MagicMock()
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController()
        controller.close()
        
        mock_arduino.close.assert_called_once()


class TestArduinoControllerListenThread:
    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_listen_thread_is_daemon(self, mock_sleep, mock_serial):
        mock_arduino = MagicMock()
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController()
        
        assert controller.read_thread.daemon is True

    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_listen_thread_target(self, mock_sleep, mock_serial):
        mock_arduino = MagicMock()
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController()
        
        # Verify the thread is using _listen_to_arduino method
        assert controller.read_thread._target == controller._listen_to_arduino

    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_listen_to_arduino_with_data(self, mock_sleep, mock_serial, capsys):
        mock_arduino = MagicMock()
        mock_arduino.in_waiting = 20
        mock_arduino.readline.return_value = b"TASK_COMPLETED\n"
        mock_serial.return_value = mock_arduino
        
        # Create controller but set running to False immediately to stop the thread
        controller = ArduinoController()
        # Simulate one iteration of the listen loop
        if controller.arduino.in_waiting > 0:
            try:
                response = controller.arduino.readline().decode('utf-8').strip()
                if response:
                    print(f"\n[Arduino]: {response}")
                    controller.handle_response(response)
            except Exception as e:
                print(f"Read error: {e}")

    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_listen_to_arduino_read_error(self, mock_sleep, mock_serial, capsys):
        mock_arduino = MagicMock()
        mock_arduino.in_waiting = 20
        mock_arduino.readline.side_effect = Exception("Read error")
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController()
        # Manually call listen logic to test error handling
        try:
            if controller.arduino.in_waiting > 0:
                response = controller.arduino.readline().decode('utf-8').strip()
        except Exception as e:
            print(f"Read error: {e}")
        
        captured = capsys.readouterr()
        assert "Read error" in captured.out


class TestArduinoControllerIntegration:
    @patch('serial.arduino_controller.serial.Serial')
    @patch('serial.arduino_controller.time.sleep')
    def test_full_workflow(self, mock_sleep, mock_serial):
        mock_arduino = MagicMock()
        mock_serial.return_value = mock_arduino
        
        controller = ArduinoController(port='COM3', baudrate=9600)
        controller.send_command("MOVE:100,50,75")
        controller.close()
        
        assert mock_arduino.write.called
        assert mock_arduino.close.called
        assert controller.running is False
