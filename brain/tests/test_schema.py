import pytest
from typing import Optional
from unittest.mock import patch, MagicMock
from pydantic import BaseModel
from planner.schema import (
    Intent,
    RobotCommandSchema,
    get_commands_list_schema,
    get_classifier_schema,
)


class TestIntentEnum:
    def test_intent_values(self):
        assert Intent.PICK_UP == "pick_up"
        assert Intent.DROP_OFF == "drop_off"
        assert Intent.MOVE_TO == "move_to"
        assert Intent.HOME == "home"
        assert Intent.STOP == "stop"
        assert Intent.WAVE == "wave"

    def test_all_intents_exist(self):
        intents = [Intent.PICK_UP, Intent.DROP_OFF, Intent.MOVE_TO, Intent.HOME, Intent.STOP, Intent.WAVE]
        assert len(intents) == 6


class TestRobotCommandSchema:
    def test_robot_command_schema_valid(self):
        command = RobotCommandSchema(
            step_number=0,
            action=Intent.PICK_UP,
            target_object="cup",
            grip_strength=75
        )
        assert command.step_number == 0
        assert command.action == Intent.PICK_UP
        assert command.target_object == "cup"
        assert command.grip_strength == 75

    def test_robot_command_schema_default_values(self):
        command = RobotCommandSchema(
            step_number=1,
            action=Intent.MOVE_TO,
        )
        assert command.step_number == 1
        assert command.action == Intent.MOVE_TO
        assert command.target_object is None
        assert command.grip_strength == 50

    def test_robot_command_schema_invalid_action(self):
        with pytest.raises(ValueError):
            RobotCommandSchema(
                step_number=0,
                action="invalid_action"
            )

    def test_robot_command_schema_missing_step_number(self):
        with pytest.raises(ValueError):
            RobotCommandSchema(action=Intent.HOME)

    def test_robot_command_schema_grip_strength_range(self):
        command = RobotCommandSchema(
            step_number=0,
            action=Intent.PICK_UP,
            grip_strength=100
        )
        assert command.grip_strength == 100

    def test_robot_command_schema_all_intents(self):
        for intent in [Intent.PICK_UP, Intent.DROP_OFF, Intent.MOVE_TO, Intent.HOME, Intent.STOP, Intent.WAVE]:
            command = RobotCommandSchema(
                step_number=0,
                action=intent
            )
            assert command.action == intent


class TestGetCommandsListSchema:
    def test_get_commands_list_schema_structure(self):
        schema = get_commands_list_schema(RobotCommandSchema)
        
        assert hasattr(schema, 'model_fields')
        assert 'action_description' in schema.model_fields
        assert 'commands' in schema.model_fields

    def test_get_commands_list_schema_creates_instance(self):
        schema = get_commands_list_schema(RobotCommandSchema)
        
        instance = schema(
            action_description="Pick up the cup",
            commands=[
                {
                    "step_number": 0,
                    "action": "pick_up",
                    "target_object": "cup",
                    "grip_strength": 75
                }
            ]
        )
        
        assert instance.action_description == "Pick up the cup"
        assert len(instance.commands) == 1

    def test_get_commands_list_schema_multiple_commands(self):
        schema = get_commands_list_schema(RobotCommandSchema)
        
        instance = schema(
            action_description="Complex task",
            commands=[
                {
                    "step_number": 0,
                    "action": "pick_up",
                    "target_object": "cup",
                },
                {
                    "step_number": 1,
                    "action": "move_to",
                    "target_object": None,
                },
                {
                    "step_number": 2,
                    "action": "drop_off",
                }
            ]
        )
        
        assert len(instance.commands) == 3


class TestGetClassifierSchema:
    def test_get_classifier_schema_basic(self):
        available_objects = ["cup", "ball"]
        schema = get_classifier_schema(available_objects)
        
        instance = schema(
            step_number=0,
            action=Intent.PICK_UP,
            target_object="cup"
        )
        
        assert instance.target_object == "cup"

    def test_get_classifier_schema_includes_no_object(self):
        available_objects = ["cup"]
        schema = get_classifier_schema(available_objects)
        
        instance = schema(
            step_number=0,
            action=Intent.MOVE_TO,
            target_object="no_object"
        )
        
        assert instance.target_object == "no_object"

    def test_get_classifier_schema_default_no_object(self):
        available_objects = []
        schema = get_classifier_schema(available_objects)
        
        instance = schema(
            step_number=0,
            action=Intent.HOME,
        )
        
        assert instance.target_object == "no_object"

    def test_get_classifier_schema_multiple_objects(self):
        available_objects = ["cup", "ball", "block", "cylinder"]
        schema = get_classifier_schema(available_objects)
        
        for obj in available_objects:
            instance = schema(
                step_number=0,
                action=Intent.PICK_UP,
                target_object=obj
            )
            assert instance.target_object == obj

    def test_get_classifier_schema_rejects_invalid_object(self):
        available_objects = ["cup", "ball"]
        schema = get_classifier_schema(available_objects)
        
        with pytest.raises(ValueError):
            schema(
                step_number=0,
                action=Intent.PICK_UP,
                target_object="invalid_object"
            )

    def test_get_classifier_schema_empty_objects_list(self):
        schema = get_classifier_schema([])
        
        instance = schema(
            step_number=0,
            action=Intent.STOP
        )
        
        assert instance.action == Intent.STOP

    def test_get_classifier_schema_inherits_base_schema(self):
        available_objects = ["cup"]
        schema = get_classifier_schema(available_objects)
        
        instance = schema(
            step_number=5,
            action=Intent.WAVE,
            grip_strength=90
        )
        
        assert instance.step_number == 5
        assert instance.grip_strength == 90
