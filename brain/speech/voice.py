import speech_recognition as sr
from config import TOOL_CONFIG

recognizer = sr.Recognizer()

def capture_speech() -> str:

    if TOOL_CONFIG["WHISPER_PAUSE_THRESHOLD"] is not None:
        # set pause threshold or use default
        recognizer.pause_threshold = TOOL_CONFIG["WHISPER_PAUSE_THRESHOLD"]

    with sr.Microphone() as source:
        print("Adjusting for background noise... Please wait 1 second.")
        # Dynamically tunes the energy threshold based on surrounding room noise
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("Capturing speech...")
        audio = recognizer.listen(source)

    try:
        extracted_text = recognizer.recognize_whisper(audio, language="english")
        print("Text: " + extracted_text)
        return extracted_text
    except sr.UnknownValueError:
        print("Whisper could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Whisper; {e}")
        return ""
    except Exception as e:
        print(f"Speech capture error: {e}")
        return ""