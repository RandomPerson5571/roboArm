import pytest
from unittest.mock import patch, MagicMock
from speech.text_to_speech import announce_actions


class TestAnnounceActions:
    @patch('speech.text_to_speech.engine')
    def test_announce_actions_basic(self, mock_engine):
        announce_actions("Test announcement")
        
        mock_engine.say.assert_called_once_with("Test announcement")
        mock_engine.runAndWait.assert_called_once()

    @patch('speech.text_to_speech.engine')
    def test_announce_actions_empty_string(self, mock_engine):
        announce_actions("")
        
        mock_engine.say.assert_called_once_with("")
        mock_engine.runAndWait.assert_called_once()

    @patch('speech.text_to_speech.engine')
    def test_announce_actions_long_text(self, mock_engine):
        long_text = "The robot is now picking up the blue cup and moving to the drop-off location. Please stand back."
        announce_actions(long_text)
        
        mock_engine.say.assert_called_once_with(long_text)
        mock_engine.runAndWait.assert_called_once()

    @patch('speech.text_to_speech.engine')
    def test_announce_actions_special_characters(self, mock_engine):
        text_with_special = "Ready! 3... 2... 1... Go!"
        announce_actions(text_with_special)
        
        mock_engine.say.assert_called_once_with(text_with_special)

    @patch('speech.text_to_speech.engine')
    def test_announce_actions_multiple_calls(self, mock_engine):
        announce_actions("First message")
        announce_actions("Second message")
        
        assert mock_engine.say.call_count == 2
        assert mock_engine.runAndWait.call_count == 2

    @patch('speech.text_to_speech.engine')
    def test_announce_actions_unicode(self, mock_engine):
        text_with_unicode = "Robot status: ✓ Ready"
        announce_actions(text_with_unicode)
        
        mock_engine.say.assert_called_once_with(text_with_unicode)

    @patch('speech.text_to_speech.engine')
    def test_announce_actions_calls_order(self, mock_engine):
        announce_actions("Testing order")
        
        # Verify say is called before runAndWait
        call_order = [call[0] for call in mock_engine.mock_calls]
        say_index = next(i for i, call in enumerate(call_order) if 'say' in str(call))
        wait_index = next(i for i, call in enumerate(call_order) if 'runAndWait' in str(call))
        assert say_index < wait_index

    @patch('speech.text_to_speech.engine')
    def test_announce_actions_with_numbers(self, mock_engine):
        text = "Coordinates: X=50, Y=30, Z=100"
        announce_actions(text)
        
        mock_engine.say.assert_called_once_with(text)

    @patch('speech.text_to_speech.engine')
    def test_announce_actions_with_punctuation(self, mock_engine):
        text = "Task completed successfully! Ready for next command?"
        announce_actions(text)
        
        mock_engine.say.assert_called_once_with(text)

    @patch('speech.text_to_speech.engine')
    def test_announce_actions_single_word(self, mock_engine):
        announce_actions("Moving")
        
        mock_engine.say.assert_called_once_with("Moving")
        mock_engine.runAndWait.assert_called_once()


class TestAnnounceActionsIntegration:
    @patch('speech.text_to_speech.engine')
    def test_announce_multiple_status_messages(self, mock_engine):
        messages = [
            "Robot initialized",
            "Camera ready",
            "Starting task",
            "Task completed"
        ]
        
        for msg in messages:
            announce_actions(msg)
        
        assert mock_engine.say.call_count == 4
        assert mock_engine.runAndWait.call_count == 4

    @patch('speech.text_to_speech.engine')
    def test_announce_error_message(self, mock_engine):
        announce_actions("Error: No object detected")
        
        mock_engine.say.assert_called_once_with("Error: No object detected")
