from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

import os
import time
import requests
from dotenv import load_dotenv

# ---------------------------------------
#  ENV + CLIENTS
# ---------------------------------------
load_dotenv()

print("FASTAPI ELEVEN KEY:", os.getenv("ELEVENLABS_API_KEY"))
print("FASTAPI VOICE:", os.getenv("ELEVEN_VOICE_ID"))


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID", "")  # will validate at runtime

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing from .env")

from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Optional ElevenLabs SDK
try:
    from elevenlabs import generate, set_api_key

    if ELEVENLABS_API_KEY:
        set_api_key(ELEVENLABS_API_KEY)
        _ELEVEN_SDK_AVAILABLE = True
    else:
        _ELEVEN_SDK_AVAILABLE = False
except Exception:
    _ELEVEN_SDK_AVAILABLE = False


# ---------------------------------------
#  CREATE APP
# ---------------------------------------
app = FastAPI()

# CORS (open for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static + templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ---------------------------------------
#  GLOBAL STATE
# ---------------------------------------
toshi_mode_enabled = False
last_ai_generation = 0.0
AI_COOLDOWN = 25  # seconds


# ---------------------------------------
#  HELPERS: EXTERNAL DATA
# ---------------------------------------
def fetch_usd_to_jpy() -> float | None:
    """Fetch live USD→JPY rate."""
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        r.raise_for_status()
        return r.json()["rates"]["JPY"]
    except Exception as e:
        print("FX API error:", e)
        return None


def fetch_toshi_price() -> float | None:
    """Fetch live Toshi price in USD from CoinGecko."""
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=toshi&vs_currencies=usd",
            timeout=10,
        )
        r.raise_for_status()
        return r.json()["toshi"]["usd"]
    except Exception as e:
        print("Toshi API error:", e)
        return None


# ---------------------------------------
#  TOSHI AI REPLY
# ---------------------------------------
def generate_ai_reply(amount: float, usd_to_jpy: float, toshi_price: float) -> str:
    """Generate flirty Toshi-chan reply based on conversion data."""
    global last_ai_generation

    now = time.time()
    if now - last_ai_generation < AI_COOLDOWN:
        return "Toshi-chan is still speaking… 🦊💗 Give her a moment, Senpai!"

    last_ai_generation = now

    jpy = amount * usd_to_jpy
    toshi_amount = amount / toshi_price if toshi_price else 0

    prompt = f"""
You are **Toshi-chan 💗**, a sweet, flirty anime catgirl who loves meme coins.
You ALWAYS call the user **Senpai**.

You MUST include ALL of the following in your reply:

1. The EXACT number of Toshi coins Senpai would get: **{toshi_amount}**
2. The exact USD amount Senpai entered: **${amount}**
3. The exact JPY value of that amount: **¥{jpy}**
4. The current Toshi price in USD: **${toshi_price}**
5. Whether you think it's a good time to buy or wait, based on meme coin vibes and simple trend vibes (keep it fun, not financial advice).
6. A cute, playful, flirty emotional reaction (blushing, purring, tail wagging, etc.).
7. Some encouragement for Senpai.

Tone:
- Cute
- Flirty
- Anime energy
- Use emojis like 💗🦊✨
- Max 3–5 sentences.
"""

    try:
        res = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
        )
        text = res.output[0].content[0].text

        # Safety net: if the Toshi amount doesn't show up, append it
        if str(round(toshi_amount))[:3] not in text:
            text += f"\n\n(Toshi-chan adds: You would get **{toshi_amount} Toshi**, Senpai! 💗🦊)"

        return text
    except Exception as e:
        print("🔥 Toshi AI error:", e)
        return "Toshi-chan’s tail got tangled… try again in a bit, Senpai 💗"


# ---------------------------------------
#  ELEVENLABS REST FALLBACK
# ---------------------------------------
def _elevenlabs_tts_rest(text: str, voice_id: str, out_path: str = "static/toshi_tts.mp3"):
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY not set")

    if not voice_id:
        raise RuntimeError("ELEVEN_VOICE_ID not set or invalid")

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = {"text": text}

    try:
        with requests.post(tts_url, json=payload, headers=headers, timeout=30, stream=True) as r:
            r.raise_for_status()
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)
    except requests.HTTPError as e:
        # Log body for 401/debug
        print("🔥 ElevenLabs REST error:", e, getattr(e.response, "text", ""))
        raise

    return out_path


# ---------------------------------------
#  ROUTES
# ---------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve main Toshi converter page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/toshi_mode")
async def toggle_toshi():
    """Toggle Toshi-mode on/off."""
    global toshi_mode_enabled
    toshi_mode_enabled = not toshi_mode_enabled
    return {"toshi_mode": toshi_mode_enabled}


@app.post("/api/convert")
async def convert(data: dict):
    """
    Main conversion endpoint.
    Expected JSON:
    {
        "amount": 100,
        "toshi_mode": true/false
    }
    """
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        return {"error": "Invalid amount"}

    usd_to_jpy = fetch_usd_to_jpy()
    toshi_price = fetch_toshi_price()

    if usd_to_jpy is None:
        return {"error": "FX API unavailable"}
    if toshi_price is None:
        return {"error": "Toshi price unavailable"}

    jpy = amount * usd_to_jpy
    toshi_amount = amount / toshi_price if toshi_price else 0

    if data.get("toshi_mode", False):
        ai_reply = generate_ai_reply(amount, usd_to_jpy, toshi_price)
    else:
        ai_reply = "Toshi is thinking… 💗 (Enable Toshi Mode for a flirty analysis, Senpai!)"

    return {
        "usd_to_jpy": usd_to_jpy,
        "toshi_price": toshi_price,
        "jpy": jpy,
        "toshi_amount": toshi_amount,
        "ai_reply": ai_reply,
    }


@app.post("/api/chat")
async def chat(message: str = Form(...)):
    """
    Simple free-form Toshi-chan chat.
    Frontend should POST form-data: { message: "..." }
    """
    prompt = f"""
You are Toshi-chan 💗 — a playful anime catgirl who loves meme coins.
You ALWAYS call the user Senpai.

User message:
{message}

Reply as Toshi-chan in 2–4 sentences:
- flirty
- cute
- supportive
- reference Toshi/meme coins if it makes sense
"""

    try:
        res = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
        )
        reply = res.output[0].content[0].text
    except Exception as e:
        print("🔥 Chat error:", e)
        reply = "Toshi-chan’s tail got tangled… try again, Senpai 💗"

    return {"reply": reply}


@app.post("/api/tts")
async def tts(payload: dict):
    text = payload.get("text", "")
    if not text:
        return {"error": "No text provided"}

    if not ELEVENLABS_API_KEY:
        return {"error": "ELEVENLABS_API_KEY missing"}

    if not ELEVEN_VOICE_ID:
        return {"error": "ELEVEN_VOICE_ID missing"}

    out_path = "static/toshi_tts.mp3"

    try:
        # REST API for stability
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}",
            json={"text": text},
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg"
            },
            stream=True,
            timeout=30
        )

        r.raise_for_status()

        # Save audio
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(1024 * 16):
                f.write(chunk)

        # Return audio file
        return FileResponse(out_path, media_type="audio/mpeg")

    except Exception as e:
        print("🔥 ElevenLabs error:", e)
        return {"error": str(e)}

# For Gunicorn / deployment (optional)
application = app
