from pydantic import BaseModel, Field, create_model
from typing import Literal, Optional, List
from enum import StrEnum

class Intent(StrEnum):
    PICK_UP = "pick_up"
    DROP_OFF = "drop_off"
    MOVE_TO = "move_to"
    HOME = "home"
    STOP = "stop"
    WAVE = "wave"

class RobotIntents(StrEnum):
    STOP = "stop"
    WAVE = "wave"
    PICK_UP = "pick_up"
    DROP_OFF = "drop_off"

class RobotCommandSchema(BaseModel):
    action: RobotIntents = Field(
        description="The primary physical action the robot arm must perform."
    )
    target_object: Optional[str] = Field(
        default="no_object", 
        description="The name of the item to interact with (e.g., 'cup', 'ball'). If there isn't a object that matches closely with the voice command, default to none or 'no_object'."
    )
    grip_strength: int = Field(
        default=50, 
        description="The grip strength multiplier for the joints, from 10 to 100."
    )


def get_commands_list_schema(command_schema: BaseModel) -> BaseModel:
    ListSchema = create_model(
        "RobotCommandsListSchema",
        action_description=(str, Field(
            description="Describe the actions you are going to do"
        )),
        commands=(List[command_schema], Field(
            description="A list of classified commands"
        ))
    )

    return ListSchema

def get_classifier_schema(available_objects: list[str]) -> BaseModel:
    # Normalize and dedupe object names, then ensure "no_object" is always allowed.
    unique_objects = tuple(dict.fromkeys(available_objects))
    allowed_values = unique_objects + ("no_object",)
    DynamicLiteral = Literal[allowed_values] # type: ignore

    # Override the target_object field with the new type constraint.
    DynamicSchema = create_model(
        "RobotCommandSchema",
        __base__=RobotCommandSchema,
        target_object=(Optional[DynamicLiteral], Field(
            default="no_object", 
            description="The name of the item to interact with. Must be one of the available objects or 'no_object'."
        ))
    )

    return DynamicSchema