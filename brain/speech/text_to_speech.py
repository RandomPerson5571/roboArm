import pyttsx3

from config import TOOL_CONFIG

engine = pyttsx3.init()
engine.setProperty("volume", TOOL_CONFIG["TTS_VOLUME"] or 1.0)
engine.setProperty("rate", TOOL_CONFIG["TTS_RATE"] or 180)

def announce_actions(text: str):
   engine.say(text)
   engine.runAndWait()


def announce_status(message: str) -> None:
    print(message)
    announce_actions(message)