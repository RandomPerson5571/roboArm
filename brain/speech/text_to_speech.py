from config import TOOL_CONFIG

from gtts import gTTS
import os

language = TOOL_CONFIG.get("Language", "en")

def announce_actions(text: str):
   tts = gTTS(text=text, lang=language, slow=False)

   # Save the speech into an MP3 file
   audio_file = "output.mp3"
   tts.save(audio_file)

   os.system(f"start {audio_file}")  # Use 'open' instead of 'start' on macOS


def announce_status(message: str) -> None:
    print(message)
   #  announce_actions(message)