import pytest
from unittest.mock import patch, MagicMock
import speech_recognition as sr
from speech.voice import capture_speech


class TestCaptureSpeech:
    @patch('speech.voice.recognizer')
    @patch('speech.voice.sr.Microphone')
    def test_capture_speech_success(self, mock_microphone, mock_recognizer):
        # Mock the microphone context manager
        mock_source = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        # Mock audio capture
        mock_audio = MagicMock()
        mock_recognizer.listen.return_value = mock_audio
        
        # Mock successful recognition
        mock_recognizer.recognize_whisper.return_value = "pick up the cup"
        
        result = capture_speech()
        
        assert result == "pick up the cup"
        mock_recognizer.listen.assert_called_once_with(mock_source)
        mock_recognizer.recognize_whisper.assert_called_once_with(mock_audio, language="english")

    @patch('speech.voice.recognizer')
    @patch('speech.voice.sr.Microphone')
    def test_capture_speech_unknown_value_error(self, mock_microphone, mock_recognizer):
        mock_source = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        mock_audio = MagicMock()
        mock_recognizer.listen.return_value = mock_audio
        
        # Mock UnknownValueError
        mock_recognizer.recognize_whisper.side_effect = sr.UnknownValueError()
        
        result = capture_speech()
        
        assert result == ""

    @patch('speech.voice.recognizer')
    @patch('speech.voice.sr.Microphone')
    def test_capture_speech_request_error(self, mock_microphone, mock_recognizer):
        mock_source = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        mock_audio = MagicMock()
        mock_recognizer.listen.return_value = mock_audio
        
        # Mock RequestError
        mock_recognizer.recognize_whisper.side_effect = sr.RequestError("Connection failed")
        
        result = capture_speech()
        
        assert result == ""

    @patch('speech.voice.recognizer')
    @patch('speech.voice.sr.Microphone')
    def test_capture_speech_generic_exception(self, mock_microphone, mock_recognizer):
        mock_source = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        mock_audio = MagicMock()
        mock_recognizer.listen.return_value = mock_audio
        
        # Mock generic exception
        mock_recognizer.recognize_whisper.side_effect = Exception("Unexpected error")
        
        result = capture_speech()
        
        assert result == ""

    @patch('speech.voice.TOOL_CONFIG', {'WHISPER_PAUSE_THRESHOLD': 1.0})
    @patch('speech.voice.recognizer')
    @patch('speech.voice.sr.Microphone')
    def test_capture_speech_with_pause_threshold(self, mock_microphone, mock_recognizer):
        mock_source = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        mock_audio = MagicMock()
        mock_recognizer.listen.return_value = mock_audio
        mock_recognizer.recognize_whisper.return_value = "hello"
        
        capture_speech()
        
        assert mock_recognizer.pause_threshold == 1.0

    @patch('speech.voice.TOOL_CONFIG', {'WHISPER_PAUSE_THRESHOLD': None})
    @patch('speech.voice.recognizer')
    @patch('speech.voice.sr.Microphone')
    def test_capture_speech_without_pause_threshold(self, mock_microphone, mock_recognizer):
        mock_source = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        mock_audio = MagicMock()
        mock_recognizer.listen.return_value = mock_audio
        mock_recognizer.recognize_whisper.return_value = "hello"
        
        capture_speech()
        
        # pause_threshold should not be set
        mock_recognizer.adjust_for_ambient_noise.assert_called_once()

    @patch('speech.voice.recognizer')
    @patch('speech.voice.sr.Microphone')
    def test_capture_speech_adjusts_for_noise(self, mock_microphone, mock_recognizer):
        mock_source = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        mock_audio = MagicMock()
        mock_recognizer.listen.return_value = mock_audio
        mock_recognizer.recognize_whisper.return_value = "test"
        
        capture_speech()
        
        mock_recognizer.adjust_for_ambient_noise.assert_called_once_with(mock_source, duration=1)

    @patch('speech.voice.recognizer')
    @patch('speech.voice.sr.Microphone')
    def test_capture_speech_returns_text(self, mock_microphone, mock_recognizer):
        mock_source = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        mock_audio = MagicMock()
        mock_recognizer.listen.return_value = mock_audio
        
        expected_text = "move the block to the left"
        mock_recognizer.recognize_whisper.return_value = expected_text
        
        result = capture_speech()
        
        assert result == expected_text

    @patch('speech.voice.recognizer')
    @patch('speech.voice.sr.Microphone')
    def test_capture_speech_listens_with_correct_source(self, mock_microphone, mock_recognizer):
        mock_source = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        mock_audio = MagicMock()
        mock_recognizer.listen.return_value = mock_audio
        mock_recognizer.recognize_whisper.return_value = "test"
        
        capture_speech()
        
        # Verify listen is called with the microphone source
        mock_recognizer.listen.assert_called_once_with(mock_source)

    @patch('speech.voice.TOOL_CONFIG', {'WHISPER_PAUSE_THRESHOLD': 0.5})
    @patch('speech.voice.recognizer')
    @patch('speech.voice.sr.Microphone')
    def test_capture_speech_custom_pause_threshold(self, mock_microphone, mock_recognizer):
        mock_source = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        mock_audio = MagicMock()
        mock_recognizer.listen.return_value = mock_audio
        mock_recognizer.recognize_whisper.return_value = "test"
        
        capture_speech()
        
        assert mock_recognizer.pause_threshold == 0.5

    @patch('speech.voice.recognizer')
    @patch('speech.voice.sr.Microphone')
    def test_capture_speech_language_english(self, mock_microphone, mock_recognizer):
        mock_source = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        mock_audio = MagicMock()
        mock_recognizer.listen.return_value = mock_audio
        mock_recognizer.recognize_whisper.return_value = "test"
        
        capture_speech()
        
        # Verify language is set to english
        call_kwargs = mock_recognizer.recognize_whisper.call_args[1]
        assert call_kwargs['language'] == 'english'


class TestCaptureSpeechIntegration:
    @patch('speech.voice.recognizer')
    @patch('speech.voice.sr.Microphone')
    def test_capture_speech_full_workflow(self, mock_microphone, mock_recognizer):
        mock_source = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        mock_audio = MagicMock()
        mock_recognizer.listen.return_value = mock_audio
        mock_recognizer.recognize_whisper.return_value = "complete sentence"
        
        result = capture_speech()
        
        assert result == "complete sentence"
        mock_recognizer.adjust_for_ambient_noise.assert_called_once()
        mock_recognizer.listen.assert_called_once()
        mock_recognizer.recognize_whisper.assert_called_once()

    @patch('speech.voice.recognizer')
    @patch('speech.voice.sr.Microphone')
    def test_capture_speech_error_handling_order(self, mock_microphone, mock_recognizer):
        mock_source = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        mock_audio = MagicMock()
        mock_recognizer.listen.return_value = mock_audio
        
        # Test that UnknownValueError is caught before RequestError
        mock_recognizer.recognize_whisper.side_effect = sr.UnknownValueError()
        result = capture_speech()
        assert result == ""
