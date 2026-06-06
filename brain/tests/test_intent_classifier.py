import pytest
import json
from unittest.mock import patch, MagicMock
from planner.intent_classifier import classify_intent


class TestClassifyIntent:
    @patch('planner.intent_classifier.ollama.chat')
    @patch('planner.intent_classifier.get_commands_list_schema')
    @patch('planner.intent_classifier.get_classifier_schema')
    def test_classify_intent_valid_response(self, mock_get_class_schema, mock_get_list_schema, mock_ollama):
        # Mock the schema
        mock_schema = MagicMock()
        mock_class_schema = MagicMock()
        mock_get_classifier_schema.return_value = mock_class_schema
        mock_get_list_schema.return_value = mock_schema
        mock_schema.model_json_schema.return_value = {"type": "object"}
        
        # Mock ollama response
        response_dict = {"commands": [{"action": "pick_up"}]}
        mock_ollama.return_value = {
            'message': {'content': json.dumps(response_dict)}
        }
        
        result = classify_intent("pick up the cup", ["cup", "ball"])
        
        assert result == response_dict
        mock_ollama.assert_called_once()
        mock_get_classifier_schema.assert_called_once_with(["cup", "ball"])

    @patch('planner.intent_classifier.ollama.chat')
    @patch('planner.intent_classifier.get_commands_list_schema')
    @patch('planner.intent_classifier.get_classifier_schema')
    def test_classify_intent_with_empty_objects_list(self, mock_get_class_schema, mock_get_list_schema, mock_ollama):
        mock_schema = MagicMock()
        mock_class_schema = MagicMock()
        mock_get_classifier_schema.return_value = mock_class_schema
        mock_get_list_schema.return_value = mock_schema
        mock_schema.model_json_schema.return_value = {"type": "object"}
        
        response_dict = {"commands": [{"action": "home"}]}
        mock_ollama.return_value = {
            'message': {'content': json.dumps(response_dict)}
        }
        
        result = classify_intent("go home", [])
        
        assert result == response_dict
        mock_get_classifier_schema.assert_called_once_with([])

    @patch('planner.intent_classifier.ollama.chat')
    @patch('planner.intent_classifier.get_commands_list_schema')
    @patch('planner.intent_classifier.get_classifier_schema')
    def test_classify_intent_with_multiple_objects(self, mock_get_class_schema, mock_get_list_schema, mock_ollama):
        mock_schema = MagicMock()
        mock_class_schema = MagicMock()
        mock_get_classifier_schema.return_value = mock_class_schema
        mock_get_list_schema.return_value = mock_schema
        mock_schema.model_json_schema.return_value = {"type": "object"}
        
        response_dict = {"commands": [{"action": "drop_off", "target_object": "cup"}]}
        mock_ollama.return_value = {
            'message': {'content': json.dumps(response_dict)}
        }
        
        objects_list = ["cup", "ball", "block", "cylinder"]
        result = classify_intent("drop it", objects_list)
        
        assert result == response_dict
        mock_get_classifier_schema.assert_called_once_with(objects_list)

    @patch('planner.intent_classifier.ollama.chat')
    @patch('planner.intent_classifier.get_commands_list_schema')
    @patch('planner.intent_classifier.get_classifier_schema')
    def test_classify_intent_invalid_json_response(self, mock_get_class_schema, mock_get_list_schema, mock_ollama):
        mock_schema = MagicMock()
        mock_class_schema = MagicMock()
        mock_get_classifier_schema.return_value = mock_class_schema
        mock_get_list_schema.return_value = mock_schema
        mock_schema.model_json_schema.return_value = {"type": "object"}
        
        mock_ollama.return_value = {
            'message': {'content': 'invalid json response'}
        }
        
        result = classify_intent("pick up", ["cup"])
        
        # When JSON parsing fails, the raw content is returned
        assert result == 'invalid json response'

    @patch('planner.intent_classifier.ollama.chat')
    @patch('planner.intent_classifier.get_commands_list_schema')
    @patch('planner.intent_classifier.get_classifier_schema')
    def test_classify_intent_system_prompt(self, mock_get_class_schema, mock_get_list_schema, mock_ollama):
        mock_schema = MagicMock()
        mock_class_schema = MagicMock()
        mock_get_classifier_schema.return_value = mock_class_schema
        mock_get_list_schema.return_value = mock_schema
        mock_schema.model_json_schema.return_value = {"type": "object"}
        
        mock_ollama.return_value = {
            'message': {'content': json.dumps({"commands": []})}
        }
        
        classify_intent("test", ["object1"])
        
        # Check that ollama.chat was called with correct structure
        call_args = mock_ollama.call_args
        assert call_args[1]['model'] == 'llama3'
        assert 'system' in [msg['role'] for msg in call_args[1]['messages']]
        assert 'user' in [msg['role'] for msg in call_args[1]['messages']]

    @patch('planner.intent_classifier.ollama.chat')
    @patch('planner.intent_classifier.get_commands_list_schema')
    @patch('planner.intent_classifier.get_classifier_schema')
    def test_classify_intent_voice_text_in_message(self, mock_get_class_schema, mock_get_list_schema, mock_ollama):
        mock_schema = MagicMock()
        mock_class_schema = MagicMock()
        mock_get_classifier_schema.return_value = mock_class_schema
        mock_get_list_schema.return_value = mock_schema
        mock_schema.model_json_schema.return_value = {"type": "object"}
        
        mock_ollama.return_value = {
            'message': {'content': json.dumps({"commands": []})}
        }
        
        voice_text = "please move the block to the left"
        classify_intent(voice_text, [])
        
        # Verify the voice text is included in the user message
        call_args = mock_ollama.call_args
        messages = call_args[1]['messages']
        user_message = next(msg for msg in messages if msg['role'] == 'user')
        assert voice_text in user_message['content']

    @patch('planner.intent_classifier.ollama.chat')
    @patch('planner.intent_classifier.get_commands_list_schema')
    @patch('planner.intent_classifier.get_classifier_schema')
    def test_classify_intent_dict_response(self, mock_get_class_schema, mock_get_list_schema, mock_ollama):
        mock_schema = MagicMock()
        mock_class_schema = MagicMock()
        mock_get_classifier_schema.return_value = mock_class_schema
        mock_get_list_schema.return_value = mock_schema
        mock_schema.model_json_schema.return_value = {"type": "object"}
        
        response_dict = {"commands": [{"action": "pick_up"}]}
        mock_ollama.return_value = {
            'message': {'content': response_dict}
        }
        
        result = classify_intent("pick up", ["cup"])
        
        # When content is already a dict, it's returned as-is
        assert result == response_dict
