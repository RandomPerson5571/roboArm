import os
import json

from dotenv import load_dotenv
from google import genai

from intent.schema import get_commands_list_schema, get_classifier_schema

load_dotenv()

# Access them securely
api_key = os.getenv("GEMENI_API_KEY")

if api_key is None:
    raise ValueError("invalid api key")

client = genai.Client(api_key=api_key)


def classify_intent(user_voice_text: str, available_objects: list[str]) -> str:

    system_prompt = (
        "You are the central intent classification system for a robotic arm. "
        "Analyze the user's voice command and extract the desired action and target object only. "
        "Do not provide explicit x/y coordinates; the robot will derive those from vision. "
        f"This is a list of available objects that the robot can interact with: {available_objects}. "
        "If the object involved in the user's voice command isn't in the list of available objects, do not include actions related to that object."
    )

    schema = get_classifier_schema(available_objects)
    list_schema = get_commands_list_schema(schema)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            system_prompt,
            f"Voice Command: '{user_voice_text}'"
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": list_schema
        }
    )

    content = response.text

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return content