import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVEN_VOICE_ID")

print("API KEY:", API_KEY)
print("VOICE ID:", VOICE_ID)

headers = {
    "xi-api-key": API_KEY
}

# 1. List voices
print("\nFetching voices…")
voices = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers)
print("Status:", voices.status_code)
print(voices.text)

# 2. Try a test TTS
print("\nTesting TTS…")
tts = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
    json={"text": "Hello Senpai, this is Toshi-chan."},
    headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
)

print("TTS Status:", tts.status_code)
print(tts.text[:500])
